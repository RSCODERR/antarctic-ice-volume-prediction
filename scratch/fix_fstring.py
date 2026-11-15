import re

path = 'antarctic-ice-volume-prediction/scratch/run_stage5_1_pipeline.py'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

# Replace \text{--} with \text{{--}}
text = text.replace(r'\text{--}', r'\text{{--}}')

with open(path, 'w', encoding='utf-8') as f:
    f.write(text)

print('Replaced \\text{--} successfully.')
