import os
from typing import List

import numpy as np
import torch
from torch.utils.data import Dataset
from torch.utils.data.dataloader import default_collate, DataLoader

from rulm.vocabulary import Vocabulary

class ChunkDataset(Dataset):
    def __init__(self,
                 vocabulary: Vocabulary,
                 input_files: List[str],
                 intermediate_directory: str,
                 max_sentence_length: int=50,
                 split: str="train",
                 reverse: bool=False,
                 chunk_size: int=1000000):
        self.vocabulary = vocabulary
        assert self.vocabulary.get_pad() == 0

        self.max_sentence_length = max_sentence_length
        self.chunk_size= chunk_size
        self.input_files = input_files
        self.intermediate_directory = intermediate_directory
        self.overall_count = 0
        self._preprocess(reverse)

        self.chunks = [os.path.join(intermediate_directory, file_name)
                       for file_name in os.listdir(intermediate_directory) if ".dat" in file_name]
        self.chunks.sort(key=lambda x: int(os.path.splitext(os.path.basename(x))[0]))

        self.current_chunk = None
        self.current_chunk_number = None

    def __iter__(self):
        for chunk_number, chunk_file_name in enumerate(self.chunks):
            self.current_chunk = np.memmap(chunk_file_name, dtype='int32', mode='r',
                                           shape=(self.chunk_size, self.max_sentence_length))
            self.current_chunk_number = chunk_number
            for sample in self.current_chunk:
                yield sample

    def __getitem__(self, index):
        chunk_number = index // self.chunk_size
        sample_number = index % self.chunk_size
        last_chunk_number = self.overall_count // self.chunk_size
        if chunk_number != self.current_chunk_number:
            chunk_file_name = os.path.join(self.intermediate_directory, "{}.dat".format(chunk_number))
            current_chunk_size = self.chunk_size if chunk_number != last_chunk_number else self.overall_count % self.chunk_size
            self.current_chunk = np.memmap(chunk_file_name, dtype='int32', mode='r',
                                           shape=(current_chunk_size, self.max_sentence_length))
            self.current_chunk_number = chunk_number
        return np.array(self.current_chunk[sample_number])

    def __len__(self):
        return self.overall_count

    def _preprocess(self, reverse: bool):
        length_file_name = os.path.join(self.intermediate_directory, ".length")
        if os.path.exists(self.intermediate_directory):
            assert os.path.exists(length_file_name)
            with open(length_file_name, "r") as r:
                self.overall_count = int(next(r).strip())
            return
        os.makedirs(self.intermediate_directory, exist_ok=True)
        chunk_count = 0
        sentence_count = 0
        overall_count = 0
        chunk = np.zeros((self.chunk_size, self.max_sentence_length), dtype="int32")
        for file_name in self.input_files:
            for sentence in self._parse_lines(file_name):
                indices = self.vocabulary.numericalize_inputs(sentence)
                indices += [self.vocabulary.get_eos()]
                indices = indices[:self.max_sentence_length]
                chunk[sentence_count][:len(indices)] = indices
                sentence_count += 1
                if sentence_count == self.chunk_size:
                    self.overall_count += self.chunk_size
                    chunk_file_name = os.path.join(self.intermediate_directory, "{}.dat".format(chunk_count))
                    f = np.memmap(chunk_file_name, dtype='int32', mode='w+',
                                  shape=(self.chunk_size, self.max_sentence_length))
                    f[:, :] = chunk[:, :]
                    chunk_count += 1
                    sentence_count = 0
                    chunk = np.zeros((self.chunk_size, self.max_sentence_length), dtype="int32")
        if sentence_count != 0:
            self.overall_count += sentence_count
            chunk = chunk[:sentence_count, :]
            chunk_file_name = os.path.join(self.intermediate_directory, "{}.dat".format(chunk_count))
            f = np.memmap(chunk_file_name, dtype='int32', mode='w+', shape=(sentence_count, self.max_sentence_length))
            f[:, :] = chunk[:, :]
        with open(length_file_name, "w") as w:
            w.write(str(self.overall_count))

    @staticmethod
    def _parse_lines(file_name):
        assert os.path.exists(file_name)
        with open(file_name, "r", encoding="utf-8") as r:
            for line in r:
                words = line.strip().split()
                yield words

def sort_batch_collate_fn(batch):
    lengths = []
    for sample in batch:
        lengths.append(len([elem for elem in sample if elem != 0]))
    max_length = max(lengths)
    batch, lengths = zip(*[(sample[:max_length], length) for sample, length in sorted(zip(batch, lengths), key=lambda x: -x[1])])
    lengths = list(lengths)
    batch = default_collate(batch)
    batch = batch.cpu().numpy()

    use_cuda = torch.cuda.is_available()
    LongTensor = torch.cuda.LongTensor if use_cuda else torch.LongTensor
    y = np.zeros((batch.shape[0], batch.shape[1]), dtype="int32")
    y[:, :-1] = batch[:, 1:]
    return {'x': torch.transpose(LongTensor(batch), 0, 1), 'lengths': lengths, 'y': torch.transpose(LongTensor(y), 0, 1)}

class ChunkDataLoader(DataLoader):
    def __init__(self, *args, **kwargs):
        super().__init__(collate_fn=sort_batch_collate_fn, *args, **kwargs)
