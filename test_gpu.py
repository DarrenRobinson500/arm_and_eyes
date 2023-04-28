
# pip3 install --upgrade torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu117

import torch

print(torch.__version__)
print(torch.cuda.is_available())

# Should give:
#   2.0.0+cu117
#   True