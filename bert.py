from transformers import BertTokenizer, BertForSequenceClassification, AutoTokenizer, AutoModel
import torch
import torch.nn as nn
from transformers import pipeline
from config import path_to_pt, path_to_txt
import time

def search_candidates(model: AutoModel, tokenizer: AutoTokenizer, batch_size, threshold: float, device: str, path_to_txt: str) -> list[str]:
    candidates = []
    with open(path_to_txt, 'r', encoding='UTF-8') as f:
        line = f.readlines()
        rows = [row.strip().replace('_', ' ') for row in line if len(row.strip()) > 0]
        for i in range(0, len(rows), batch_size):
            batch = rows[i:i + batch_size]
            inputs = tokenizer(batch, max_length=32, truncation=True, padding=True, return_tensors='pt').to(device)
            outputs = model(**inputs)
            predictions = torch.softmax(outputs.logits, dim=-1)

            for j, row in enumerate(batch):
                phrase = tokenizer.decode(inputs['input_ids'][j].tolist(), skip_special_tokens=True)
                if predictions[j][1] > threshold and len(phrase) > 2: # len(phrase) > 3 - КОСТЫЛЬ
                    candidates.append(phrase)

    for i in range(len(candidates)-1, 0, -1):
        if candidates[i][0].lower() == candidates[i][0] and candidates[i][0].isalpha():
            candidates[i-1] += ' ' + candidates[i]
            candidates[i] = ''
    candidates = [cand for cand in candidates if len(cand) > 0]
    return candidates

if __name__ == "__main__":
    start_time = time.time()
    threshold = 0.99 # <---- EXPERIMENT WITH THIS PARAMETER
    batch_size = 64 # <---- CHANGE TO len(page)
    tokenizer = BertTokenizer.from_pretrained("JamradisePalms/bert_sentence_classifier_tuned", num_labels=2,
                                              output_attentions=False, output_hidden_states=False)
    model = BertForSequenceClassification.from_pretrained("JamradisePalms/bert_sentence_classifier_tuned")
    # model.load_state_dict(torch.load(path_to_pt, weights_only=True))
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    model.to(device)
    # TODO: ADD SPELL-CHECKER
    with torch.no_grad():
        candidates = search_candidates(model, tokenizer, batch_size, threshold, device, path_to_txt)
    print(candidates)
    print('\n'.join(candidates))