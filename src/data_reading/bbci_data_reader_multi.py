from src.data_reading.base_data_reader import BaseDataReader
from braindecode.datasets.bbci import BBCIDataset
from braindecode.datautil.trial_segment import create_signal_target_from_raw_mne
from braindecode.datautil.signalproc import exponential_running_standardize
from braindecode.mne_ext.signalproc import resample_cnt, mne_apply
from collections import OrderedDict
from src.data_reading.utils import RunningStatistics
import logging
import os
import numpy as np


logger = logging.getLogger(__name__)


class HGDDataReaderMulti(BaseDataReader):
    class ExampleInfo(BaseDataReader.BaseExampleInfo):
        """
        Since those examples are quite short, it is better for validation to use full sequence size instead of
        dividing the data into chunks. Keep that in mind.
        """
        def __init__(self, example_id, random_mode, offset_size, data, label, context):
            super().__init__(example_id, random_mode=random_mode, offset_size=offset_size)

            self.label = label
            self.data = np.transpose(data)
            # Now data has shape time x features

            # No context for now for this data
            self.context = np.array([context]).astype(np.float32)

        def read_data(self, serialized):
            index, sequence_size = serialized

            # Time might be needed for some advanced models like PhasedLSTM
            time = np.reshape(np.arange(index, index + sequence_size), newshape=[sequence_size, 1])
            data = self.data[index: index+sequence_size]
            label = np.array([self.label] * sequence_size)
            return data, time, label, self.example_id, self.context

        def get_length(self):
            return self.data.shape[0]

    @staticmethod
    def add_arguments(parser):
        BaseDataReader.add_arguments(parser)
        parser.add_argument("subject_names", type=str, help="TODO")
        parser.add_argument("load_sensor_names", type=str,
                            help="Sensor names, provide without spaces and separate using comma.")
        parser.add_argument("segment_ival_ms_start", type=int, default=-500)
        parser.add_argument("segment_ival_ms_end", type=int, default=4000)
        parser.add_argument("sampling_freq", type=int, default=250)
        parser.add_argument("normalization_type", type=str, choices=['standard', 'none', 'exponential'])

    def _initialize(self, subject_names, load_sensor_names,
                    segment_ival_ms_start, segment_ival_ms_end, sampling_freq, normalization_type, **kwargs):
        folder = "BBCI-without-last-runs" if self.data_type != BaseDataReader.Test_Data else "BBCI-only-last-runs"

        self.file_names = [os.path.join(self.data_path, folder, "%s.BBCI.mat" % subject_name) for subject_name in
                           subject_names.split(',')]

        self.load_sensor_names = load_sensor_names.split(',')
        self.segment_ival_ms = [segment_ival_ms_start, segment_ival_ms_end]
        self.sampling_freq = sampling_freq
        self.normalization_type = normalization_type

    def _create_examples(self):
        name_to_code = OrderedDict([('Right', 1), ('Left', 2), ('Rest', 3), ('Feet', 4)])

        data_list_list = []
        for file_name in self.file_names:
            cnt = BBCIDataset(file_name, load_sensor_names=self.load_sensor_names).load()
            cnt = cnt.drop_channels(['STI 014'])
            cnt = resample_cnt(cnt, self.sampling_freq)
            if self.normalization_type == 'exponential':
                cnt = mne_apply(lambda a: exponential_running_standardize(a.T, init_block_size=1000,
                                                                          factor_new=0.001, eps=1e-4).T, cnt)

            data = create_signal_target_from_raw_mne(cnt, name_to_code, self.segment_ival_ms)
            data_list = [(d, l) for d, l in zip(data.X, data.y)]
            data_list = self.cv_split(data_list)

            # Normalize the data
            if self.normalization_type == 'standard':
                running_statistics = RunningStatistics(dim=data_list[0][0].shape[0], time_dimension_first=False)
                for data, label in data_list:
                    running_statistics.append(data)

                mean = running_statistics.mean_vector()
                sdev = np.clip(np.sqrt(running_statistics.var_vector()), 1e-5, None)

                logger.info('Normalize with \n mean: %s, \n sdev: %s' % (mean, sdev))
                for i in range(len(data_list)):
                    data_list[i] = ((data_list[i][0] - mean) / sdev, data_list[i][1])

            data_list_list.append(data_list)

        # Create examples for 4 classes
        for i, data_list in enumerate(data_list_list):
            for label in range(4):

                class_data_list = [data for data in data_list if data[1] == label]
                self.examples.append([HGDDataReaderMulti.ExampleInfo(example_id=str((i, label, j)),
                                                                     random_mode=self.random_mode,
                                                                     offset_size=self.offset_size,
                                                                     label=label, data=data, context=i)
                                      for (j, (data, label)) in enumerate(class_data_list)])

    @staticmethod
    # Has to be a static method, context_size is required when creating the model,
    # DataReader can't be instantiated properly before the model is created
    def context_size(**kwargs):
        return 1

    @staticmethod
    def input_size(**kwargs):
        return 3

    @staticmethod
    def output_size(**kwargs):
        return 4


if __name__ == '__main__':
    from src.utils import setup_logging
    setup_logging('/tmp', logging.DEBUG)
    data_reader = HGDDataReaderMulti(data_path='/home/schirrmr/data/',
                                     readers_count=1,
                                     batch_size=64,
                                     validation_batch_size=0,
                                     sequence_size=1125,
                                     validation_sequence_size=4500,
                                     balanced=1,
                                     random_mode=2,
                                     continuous=1,
                                     limit_examples=0,
                                     limit_duration=0,
                                     forget_state=1,
                                     train_on_full=0,
                                     cv_n=3,
                                     cv_k=2,
                                     force_parameters=0,
                                     offset_size=0,
                                     state_initializer=lambda: None,
                                     data_type=BaseDataReader.Train_Data,
                                     allow_smaller_batch=0,
                                     subject_name="BhNoMoSc1S001R01_ds10_1-12",
                                     load_sensor_names='C3,CPz,C4',
                                     segment_ival_ms_start=-500,
                                     segment_ival_ms_end=4000)

    sequence_size = 1125
    try:
        data_reader.start_readers()
        data_reader.initialize_epoch(sequence_size)

        ids, batch, time, labels, contexts = data_reader.get_batch()
    except:
        raise
    finally:
        data_reader.stop_readers()



