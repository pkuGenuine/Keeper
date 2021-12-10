import torch
import torch.nn as nn
from Childe.config import Config
from Childe.utils import Recorder, VoiceDataEnhancer, CNNDataLoader
import os
import numpy as np
from transformers import Wav2Vec2Processor, Wav2Vec2Model
from datasets import load_dataset

# import code
# dataset = load_dataset("hf-internal-testing/librispeech_asr_demo", "clean", split="validation")
# sampling_rate = dataset.features["audio"].sampling_rate
# processor = Wav2Vec2Processor.from_pretrained('facebook/wav2vec2-base-960h')
# model = Wav2Vec2Model.from_pretrained('facebook/wav2vec2-base-960h')
# # audio file is decoded on the fly
# inputs = processor(dataset[0]["audio"]["array"], sampling_rate=sampling_rate, return_tensors="pt")
# outputs = model(**inputs)
# last_hidden_states = outputs.last_hidden_state
# # print(inputs.shape, outputs.shape, last_hidden_states.shape)
# code.interact(local=locals())


class WakeUpWordCNNModel(nn.Module):
    """docstring for WakeUpWordCNNModel"""
    def __init__(self, input_size, hidden_size, labels=2):
        super(WakeUpWordCNNModel, self).__init__()
        self.relu = nn.ReLU()
        self.mp = nn.MaxPool1d(kernel_size=4)
        self.cnn_1 = nn.Conv1d(
            in_channels=1, out_channels=4, kernel_size=30, stride=10, 
            padding=10, dilation=1, groups=1, bias=True, padding_mode='zeros'
        )
        self.cnn_2 = nn.Conv1d(
            in_channels=4, out_channels=8, kernel_size=30, stride=10, 
            padding=10, dilation=1, groups=1, bias=True, padding_mode='zeros'
        )
        self.cnn_3 = nn.Conv1d(
            in_channels=8, out_channels=16, kernel_size=3, stride=2, 
            padding=1, dilation=1, groups=1, bias=True, padding_mode='zeros'
        )
        self.fc_1 = nn.Linear(32, 16)
        self.fc_2 = nn.Linear(16, labels)
        # self.sig = nn.Sigmoid()
    def forward(self, x):
        t1 = self.relu(self.mp(self.cnn_1(x)))
        # print(t1.shape) # 1 4 1000
        t2 = self.relu(self.mp(self.cnn_2(t1)))
        # print(t2.shape) # 1 8 25
        t3 = self.relu(self.mp(self.cnn_3(t2)))
        # print("Before fc", t3.shape) # 1 16 3
        t4 = self.fc_2(self.relu(self.fc_1(t3.reshape((t3.shape[0], -1)))))
        # return self.sig(t4)
        return t4

class WakeUpWordTransformerModel(nn.Module):
    def __init__(self, hidden_size, sampling_rate=Config["voice_record"]["rate"], labels=2):
        super(WakeUpWordTransformerModel, self).__init__()
        self.projector = Wav2Vec2Model.from_pretrained('facebook/wav2vec2-base-960h')
        # self.processor = Wav2Vec2Processor.from_pretrained('facebook/wav2vec2-base-960h')
        self.fc_1 = nn.Linear(768, hidden_size)
        self.fc_2 = nn.Linear(hidden_size, labels)
        self.relu = nn.ReLU()
        self.sampling_rate = sampling_rate
    def forward(self, x):
        # print(x.shape)
        # inputs = self.processor(x, sampling_rate=self.sampling_rate, return_tensors="pt")
        # print(inputs["input_values"].shape)
        outputs = self.projector(input_values=x)
        last_hidden_states = outputs.last_hidden_state
        # print(last_hidden_states.shape)
        # print(last_hidden_states.shape)
        pooled_output = last_hidden_states.mean(dim=1)
        p_hidden_states = self.relu(self.fc_1(pooled_output))

        # print(p_hidden_states.shape)
        return self.relu(self.fc_2(p_hidden_states)) 

class WakeUpWord(object):
    """docstring for WakeUpWord"""
    def __init__(self, input_size=24000, hidden_size=128, model_path="", model_exists=False):
        super(WakeUpWord, self).__init__()
        if not model_path:
            abs_dir = os.path.dirname(__file__)
            model_path = os.path.join(abs_dir, "model")
        self.model_path = model_path
        # if not model_exists:
        #     self.CNNModel = WakeUpWordCNNModel(input_size=input_size, hidden_size=hidden_size)
        # else:
        #     print("Loading model...")
        #     self.CNNModel = WakeUpWordCNNModel(input_size=input_size, hidden_size=hidden_size)
        #     self.CNNModel.load_state_dict(torch.load(os.path.join(self.model_path, "wakeup_model.ckpt")))
        if not model_exists:
            self.model = WakeUpWordTransformerModel(hidden_size=hidden_size)
        else:
            print("Loading model...")
            self.model = WakeUpWordTransformerModel(hidden_size=hidden_size)
            self.model.load_state_dict(torch.load(os.path.join(self.model_path, "wakeup_model.ckpt")))
            print("Loaded.")

        self.input_size = input_size
        self.recorder = Recorder()
        os.makedirs(model_path, exist_ok=True)

    def predict(self, x):
        outputs = self.model(torch.unsqueeze(torch.from_numpy(x), dim=0))
        _, predicted = torch.max(outputs.data, 1)
        if predicted[0] == 1:
            return True
        elif predicted[0] == 0:
            print("Not a wakeup...")
            return False
        else:
            # print("predicted", predicted[0])
            return False

    def record(self):
        print("Recording...")
        self.recorder.record(vtype="wakeup", name=self.wakeup_label)
        print("Done.")

    def train(self, wakeup_label, pos_dirs, neg_dirs, epoch=10, batch_size=32, lr=1e-5, save_model=True):

        def wav2np_chunks(file_path, label):
            # Only support singel channel, 16 deep wav file
            if not file_path.endswith(".wav"):
                return []
            enhancer = VoiceDataEnhancer()
            if label == 1:
                if not os.path.basename(file_path).startswith(wakeup_label):
                    return []
            with open(file_path, "rb") as f:
                np_chunk = np.frombuffer(f.read()[44:], dtype=np.int16)
            base_chunks = enhancer.random_trunc_or_padding([np_chunk], self.input_size)
            if label == 1:
                shift_chunks = enhancer.shift_chunk([base_chunks[0] for i in range(5)])
                # shift_chunks = enhancer.shift_chunk([base_chunks[0] for i in range(4)])
                # shift_chunks.append(base_chunks[0])
                noise_chunks = []
                for i in range(5):
                    noise_chunks.extend(shift_chunks)
                noise_chunks = enhancer.add_noise(noise_chunks)
                # for i in range(4):
                #     noise_chunks.extend(shift_chunks)
                # noise_chunks = enhancer.add_noise(noise_chunks)
                # noise_chunks.extend(shift_chunks)
                print(len(noise_chunks))
                return noise_chunks
            else:
                return enhancer.add_noise(base_chunks, noise_nums=2)

        loader = CNNDataLoader(
            file_sample_loader=wav2np_chunks, 
            paths=pos_dirs + neg_dirs,
            labels=[1 for i in range(len(pos_dirs))] + [0 for i in range(len(neg_dirs))]
        )
        # torch.utils.data.DataLoader(dataset=loader, batch_size=batch_size, shuffle=True, collate_fn=MyCollectFunc)
        train_loader = torch.utils.data.DataLoader(dataset=loader, batch_size=batch_size, shuffle=True)
        criterion = nn.CrossEntropyLoss()
        optimizer = torch.optim.Adam(self.model.parameters(), lr=lr)
        for epoch in range(epoch):
            total, total_pos, total_neg = 0, 0, 0
            correct, correct_pos, correct_neg = 0, 0, 0
            print(f"Epoch {epoch}")
            for i, l in enumerate(train_loader):
                outputs = self.model(l[0])
                # print(outputs.shape)
                loss = criterion(outputs, l[1])
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
                total += l[0].size(0)
                _, predicted = torch.max(outputs.data, 1)
                # print(predicted == l[1])
                # raise ValueError
                total_pos += (l[1] == 1).sum().item()
                total_neg += (l[1] == 0).sum().item()
                correct_pos += ((l[1] + predicted) == 2).sum().item()
                correct_neg += ((l[1] + predicted) == 0).sum().item()
                if (i + 1) % 5 == 0:
                    print(f"Batch {i}, loss: {loss.item()}")
            total = total_pos + total_neg
            correct = correct_neg + correct_pos
            print(f"Accuracy is: {100 * correct / total}% ({correct}/{total})")
            print(f"Recall   is: {100 * correct_pos / total_pos}% ({correct_pos}/{total_pos})")
            print(f"Misfired is: {100 * (total_neg - correct_neg) / total_neg}% ({correct_neg}/{total_neg})")
        if save_model:
            torch.save(self.model.state_dict(), os.path.join(self.model_path, "wakeup_model.ckpt"))

if __name__ == "__main__":
    path = os.path.join("..", "resource", "origin_voices")
    train_path = os.path.join("..", "resource", "trainning_voices")
    neg_list = ["nonwakeup", "others", "Albedo", "Diluc", "Keqing", "Hu_Tao", "Zhongli", "Kamisato_Ayaka", "Raiden_Shogun", "noise", "Xiao"]
    # wakeup = WakeUpWord(model_exists=False)
    # wakeup.train(
    #     wakeup_label = "Childe",
    #     pos_dirs = [os.path.join(path, "wakeup")],
    #     neg_dirs = [os.path.join(train_path, neg_dir) for neg_dir in neg_list],
    #     epoch = 1,
    #     lr=1e-5
    # )
    for i in range(10):
        wakeup = WakeUpWord(model_exists=True)
        wakeup.train(
            wakeup_label = "Childe",
            pos_dirs = [os.path.join(path, "wakeup")],
            neg_dirs = [os.path.join(train_path, neg_dir) for neg_dir in neg_list],
            epoch = 3,
            lr = 1e-5
        )

        