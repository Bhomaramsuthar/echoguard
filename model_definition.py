import torch
import torch.nn as nn
import torchvision.models as models

class EchoGuardCNN(nn.Module):
    def __init__(self):
        super(EchoGuardCNN, self).__init__()
        # Load the powerful ResNet18 architecture
        self.resnet = models.resnet18(weights=None) 
        
        # Modify the final output layer from 1000 classes down to 2 (Real vs Fake)
        num_ftrs = self.resnet.fc.in_features
        self.resnet.fc = nn.Linear(num_ftrs, 2)

    def forward(self, x):
        return self.resnet(x)