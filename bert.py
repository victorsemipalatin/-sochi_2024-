from transformers import BertTokenizer, BertForSequenceClassification, AutoTokenizer, AutoModel
import torch
import torch.nn as nn
from config import path_to_pt, path_to_txt


def search_candidates(model: AutoModel, tokenizer: AutoTokenizer, threshold: float, device: str, path_to_txt: str) -> list[str]:
    candidates = []
    with open(path_to_txt, 'r', encoding='UTF-8') as f:
        line = f.readline()
        rows = line.split("\n")
        for row in rows:
            inputs = tokenizer(row, max_length=32, truncation=True, padding=True, return_tensors='pt').to(device)
            outputs = model(**inputs)
            predictions = torch.softmax(outputs.logits, dim=-1)
            if predictions[0][1] > threshold:  # Можно менять порог вероятности заголовка.
                candidates.append(tokenizer.decode(inputs['input_ids'][0].tolist(), skip_special_tokens=True))
    return candidates


if __name__ == "__main__":
    threshold = 0.99
    tokenizer = BertTokenizer.from_pretrained("DeepPavlov/rubert-base-cased-sentence", num_labels=2,
                                              output_attentions=False, output_hidden_states=False)
    model = BertForSequenceClassification.from_pretrained("DeepPavlov/rubert-base-cased-sentence")
    model.load_state_dict(torch.load(path_to_pt, weights_only=True))
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    model.to(device)

    candidates = search_candidates(model, tokenizer, threshold, device, path_to_txt)
    print(candidates)
