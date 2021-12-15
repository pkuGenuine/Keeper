import torch
import torch.nn as nn
from Childe.config import Config
from Childe.utils import Recorder, VoiceDataEnhancer, CNNDataLoader
import os
import numpy as np
from transformers import Wav2Vec2Processor, Wav2Vec2Model
from datasets import load_dataset


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

    def forward(self, x):
        t1 = self.relu(self.mp(self.cnn_1(x)))
        t2 = self.relu(self.mp(self.cnn_2(t1)))
        t3 = self.relu(self.mp(self.cnn_3(t2)))
        t4 = self.fc_2(self.relu(self.fc_1(t3.reshape((t3.shape[0], -1)))))
        return t4

class WakeUpWordTransformerModel(nn.Module):

    def __init__(self, hidden_size, sampling_rate=Config["voice_record"]["rate"], labels=2):
        super(WakeUpWordTransformerModel, self).__init__()
        self.projector = Wav2Vec2Model.from_pretrained('facebook/wav2vec2-base-960h')
        self.fc_1 = nn.Linear(768, hidden_size)
        self.fc_2 = nn.Linear(hidden_size, labels)
        self.relu = nn.ReLU()
        self.sampling_rate = sampling_rate

    def forward(self, x):
        outputs = self.projector(input_values=x)
        last_hidden_states = outputs.last_hidden_state
        pooled_output = last_hidden_states.mean(dim=1)
        p_hidden_states = self.relu(self.fc_1(pooled_output))
        return self.relu(self.fc_2(p_hidden_states)) 

class WakeUpWord(object):
    """docstring for WakeUpWord"""
    def __init__(self, input_size=24000, hidden_size=128, model_path="", model_exists=False):
        super(WakeUpWord, self).__init__()
        if not model_path:
            abs_dir = os.path.dirname(__file__)
            model_path = os.path.join(abs_dir, "model")
        self.model_path = model_path
        if not model_exists:
            self.model = WakeUpWordTransformerModel(hidden_size=hidden_size)
        else:
            print("Loading model...")
            self.model = WakeUpWordTransformerModel(hidden_size=hidden_size)
            self.model.load_state_dict(torch.load(os.path.join(self.model_path, "wakeup_model.ckpt")))
            print("Loaded.")

        self.input_size = input_size
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
            return False


    def train(self, wakeup_label, pos_dirs, neg_dirs, epoch=10, batch_size=32, lr=1e-5, save_model=True, test_misfire=True):

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
                noise_chunks = []
                for i in range(5):
                    noise_chunks.extend(shift_chunks)
                noise_chunks = enhancer.add_noise(noise_chunks)
                return noise_chunks
            else:
                return enhancer.add_noise(base_chunks, noise_nums=2)

        loader = CNNDataLoader(
            file_sample_loader=wav2np_chunks, 
            paths=pos_dirs + neg_dirs,
            labels=[1 for i in range(len(pos_dirs))] + [0 for i in range(len(neg_dirs))]
        )
        train_loader = torch.utils.data.DataLoader(dataset=loader, batch_size=batch_size, shuffle=True)
        criterion = nn.CrossEntropyLoss()
        optimizer = torch.optim.Adam(self.model.parameters(), lr=lr)


        total, total_pos, total_neg = 0, 0, 0
        correct, correct_pos, correct_neg = 0, 0, 0
        if test_misfire:
            print("Calculating old misfire value......")
            for i, l in enumerate(train_loader):
                outputs = self.model(l[0])
                _, predicted = torch.max(outputs.data, 1)
                total_pos += (l[1] == 1).sum().item()
                total_neg += (l[1] == 0).sum().item()
                correct_neg += ((l[1] + predicted) == 0).sum().item()
                correct_pos += ((l[1] + predicted) == 2).sum().item()
            total = total_pos + total_neg
            correct = correct_neg + correct_pos
            old_misfire = (total_neg - correct_neg) / total_neg
            old_accuracy = correct / total
            print(f"Old accuracy is: {100 * correct / total}% ({correct}/{total})")
            print(f"Old recall   is: {100 * correct_pos / total_pos}% ({correct_pos}/{total_pos})")
            print(f"Old misfire  is: {100 * old_misfire}% ({correct_neg}/{total_neg})")
            if old_misfire < 0.015 and old_accuracy > 0.96:
                return

        for epoch in range(epoch):
            total, total_pos, total_neg = 0, 0, 0
            correct, correct_pos, correct_neg = 0, 0, 0
            print(f"Epoch {epoch}")
            for i, l in enumerate(train_loader):
                outputs = self.model(l[0])
                loss = criterion(outputs, l[1])
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
                total += l[0].size(0)
                _, predicted = torch.max(outputs.data, 1)
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
        if test_misfire and ((total_neg - correct_neg) / total_neg) > old_misfire:
            if correct / total < old_accuracy:
                return
        if save_model:
            print(f"Saving model")
            torch.save(self.model.state_dict(), os.path.join(self.model_path, "wakeup_model.ckpt"))



        