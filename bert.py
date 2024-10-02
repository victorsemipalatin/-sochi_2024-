from transformers import BertTokenizer, BertForSequenceClassification, AutoTokenizer, AutoModel
import torch


def search_candidates(model: AutoModel, tokenizer: AutoTokenizer, batch_size, threshold: float, device: str, text: str) -> list[str]:
    candidates = []
    lines = text.split()
    rows = [row.strip().replace('_', ' ') for row in lines if len(row.strip()) > 0]
    for i in range(0, len(rows), len(lines)):
        batch = rows[i:i + batch_size]
        inputs = tokenizer(batch, max_length=32, truncation=True, padding=True, return_tensors='pt').to(device)
        outputs = model(**inputs)
        predictions = torch.softmax(outputs.logits, dim=-1)

        for j in range(len(batch)):
            phrase = tokenizer.decode(inputs['input_ids'][j].tolist(), skip_special_tokens=True)
            if predictions[j][1] > threshold and len(phrase) > 2: # len(phrase) > 3 - КОСТЫЛЬ
                candidates.append(phrase)

    for i in range(len(candidates)-1, 0, -1):
        if candidates[i][0].lower() == candidates[i][0] and candidates[i][0].isalpha():
            candidates[i-1] += ' ' + candidates[i]
            candidates[i] = ''
    candidates = [cand for cand in candidates if len(cand) > 0]
    return candidates


def get_key_words(text):
    with torch.no_grad():
        candidates = search_candidates(model, tokenizer, batch_size, threshold, device, text)
    
    return candidates
   
threshold = 0.99 # <---- EXPERIMENT WITH THIS PARAMETER
batch_size = 64 # <---- CHANGE TO len(page)
tokenizer = BertTokenizer.from_pretrained("JamradisePalms/bert_sentence_classifier_tuned", num_labels=2,
                                      output_attentions=False, output_hidden_states=False)
model = BertForSequenceClassification.from_pretrained("JamradisePalms/bert_sentence_classifier_tuned")
# model.load_state_dict(torch.load(path_to_pt, weights_only=True))
device = 'cuda' if torch.cuda.is_available() else 'cpu'
model.to(device)
