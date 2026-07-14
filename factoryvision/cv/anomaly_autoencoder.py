from __future__ import annotations
from pathlib import Path
import random
import cv2
import numpy as np
import torch
from torch import nn
from torch.utils.data import DataLoader,TensorDataset
from sklearn.metrics import roc_auc_score

class TinyConvAutoencoder(nn.Module):
    def __init__(self):
        super().__init__()
        self.encoder=nn.Sequential(
            nn.Conv2d(3,8,3,stride=2,padding=1),nn.ReLU(),
            nn.Conv2d(8,16,3,stride=2,padding=1),nn.ReLU(),
        )
        self.decoder=nn.Sequential(
            nn.ConvTranspose2d(16,8,4,stride=2,padding=1),nn.ReLU(),
            nn.ConvTranspose2d(8,3,4,stride=2,padding=1),nn.Sigmoid(),
        )
    def forward(self,x): return self.decoder(self.encoder(x))

class AutoencoderAnomaly:
    def __init__(self,size=(64,64),model=None):
        self.size=size; self.model=model or TinyConvAutoencoder(); self.model.eval()
    def _tensor(self,path_or_image):
        img=cv2.imread(str(path_or_image)) if isinstance(path_or_image,(str,Path)) else path_or_image
        x=cv2.cvtColor(cv2.resize(img,self.size),cv2.COLOR_BGR2RGB).astype(np.float32)/255.0
        return torch.from_numpy(x).permute(2,0,1)
    def fit(self,paths:list[Path],epochs:int=8,batch_size:int=6,seed:int=17)->list[float]:
        torch.manual_seed(seed); np.random.seed(seed); random.seed(seed); torch.set_num_threads(1)
        ds=TensorDataset(torch.stack([self._tensor(p) for p in paths])); loader=DataLoader(ds,batch_size=batch_size,shuffle=True,generator=torch.Generator().manual_seed(seed))
        self.model.train(); opt=torch.optim.Adam(self.model.parameters(),lr=1e-3); loss_fn=nn.MSELoss(); history=[]
        for _ in range(epochs):
            losses=[]
            for (x,) in loader:
                opt.zero_grad(); y=self.model(x); loss=loss_fn(y,x); loss.backward(); opt.step(); losses.append(float(loss.detach()))
            history.append(float(np.mean(losses)))
        self.model.eval(); return history
    @torch.no_grad()
    def predict(self,img:np.ndarray)->tuple[float,np.ndarray]:
        x=self._tensor(img).unsqueeze(0); y=self.model(x); error=((y-x)**2).mean(1)[0].cpu().numpy(); heat=cv2.resize(error,(img.shape[1],img.shape[0])); return float(np.percentile(error,99)),heat.astype(np.float32)
    def evaluate(self,normal:list[Path],anomaly:list[Path])->dict:
        labels=[];scores=[]
        for p in normal: labels.append(0);scores.append(self.predict(cv2.imread(str(p)))[0])
        for p in anomaly: labels.append(1);scores.append(self.predict(cv2.imread(str(p)))[0])
        return {'image_auroc':float(roc_auc_score(labels,scores)),'normal_score_mean':float(np.mean(scores[:len(normal)])),'anomaly_score_mean':float(np.mean(scores[len(normal):]))}
    def save(self,path:Path,history:list[float]):
        path.parent.mkdir(parents=True,exist_ok=True); torch.save({'state_dict':self.model.state_dict(),'size':self.size,'history':history},path)
    @classmethod
    def load(cls,path:Path):
        payload=torch.load(path,map_location='cpu'); model=TinyConvAutoencoder(); model.load_state_dict(payload['state_dict']); return cls(tuple(payload['size']),model)
