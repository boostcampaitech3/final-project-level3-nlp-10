from transformers import TextClassificationPipeline, BertForSequenceClassification, AutoTokenizer

model = BertForSequenceClassification.from_pretrained('smilegate-ai/kor_unsmile')
tokenizer = AutoTokenizer.from_pretrained('smilegate-ai/kor_unsmile')

pipe = TextClassificationPipeline(
    model=model,
    tokenizer=tokenizer,
    device=0,     # cpu는 -1, gpu일 땐 gpu number라고 함. 처음엔 0.
    return_all_scores=True,
    )

# 0.7 이상 : 클린한 문장
# 0.7 미만 : 혐오 표현
print(pipe("지금 뭐하세요?")[0][9]['score'])
print(pipe("씨발 지금 뭐하세요?")[0][9]['score'])