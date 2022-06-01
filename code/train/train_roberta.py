import os
import torch
import numpy as np
from transformers import AutoTokenizer, AutoConfig, Trainer, TrainingArguments, AutoModelForSequenceClassification
from transformers import AutoModel
import random

from torch.utils.data import Dataset

class Wellness_Dataset(Dataset):
    def __init__(self, tokenizer):

        self.data = []
        file = open("../../data/wellness_dialog_for_text_classification.txt", 'r', encoding='utf-8')

        while True:
            line = file.readline()
            if not line:
                break
            datas = line.split("    ")

            tokenized_sentence = tokenizer(
                datas[0],
                return_tensors="pt",
                padding="max_length",
                truncation=True,
                max_length=512,
                return_token_type_ids = False
                )
        
            data = {
                    'input_ids': torch.tensor(tokenized_sentence['input_ids'])[0],
                    'attention_mask': torch.tensor(tokenized_sentence['attention_mask'])[0],
                    'labels': torch.tensor(int(datas[1][:-1]))
                    }

            self.data.append(data)

        file.close()

    def __len__(self):
        return len(self.data)

    def __getitem__(self,index):
        item = self.data[index]
        return item


def seed_everything(seed):
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)  # if use multi-GPU
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    np.random.seed(seed)
    random.seed(seed)        

def train():

  device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
 
  MODEL_NAME = "klue/roberta-large"
  config = AutoConfig.from_pretrained(MODEL_NAME)
  config.num_labels = 359
  model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME, config=config)
  tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

  model.to(device)

  training_args = TrainingArguments(
    output_dir='./results_roberta',          # output directory
    num_train_epochs=20,              # total number of training epochs
    learning_rate=3e-6,               # learning_rate
    per_device_train_batch_size=8,  # batch size per device during training
    fp16=True,
  )

  trainer = Trainer(
    model=model,                         
    args=training_args,               
    train_dataset=Wellness_Dataset(tokenizer=tokenizer)
  )

  trainer.train()
  
  torch.save(model.state_dict(), os.path.join(f'../model', 'roberta_model.bin'))

def main():
  train()

if __name__ == '__main__':
  seed_everything(42) 
  main()