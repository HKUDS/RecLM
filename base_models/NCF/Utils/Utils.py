import torch
import torch.nn.functional as F

def innerProduct(usrEmbeds, itmEmbeds):
	return torch.sum(usrEmbeds * itmEmbeds, dim=-1)

def pairPredict(ancEmbeds, posEmbeds, negEmbeds):
	return innerProduct(ancEmbeds, posEmbeds) - innerProduct(ancEmbeds, negEmbeds)

def calcRegLoss(model):
	ret = 0
	for W in model.parameters():
		ret += W.norm(2).square()
	return ret

def calcRegLossSingle(param):
	ret = param.norm(2).square()
	return ret

def calcReward(bprLossDiff, keepRate):
	_, posLocs = torch.topk(bprLossDiff, int(bprLossDiff.shape[0] * (1 - keepRate)))
	reward = torch.zeros_like(bprLossDiff).cuda()
	reward[posLocs] = 1.0
	return reward

def calcGradNorm(model):
	ret = 0
	for p in model.parameters():
		if p.grad is not None:
			ret += p.grad.data.norm(2).square()
	ret = (ret ** 0.5)
	ret.detach()
	return ret

def contrastLoss(embeds1, embeds2, nodes, temp):
	embeds1 = F.normalize(embeds1, p=2)
	embeds2 = F.normalize(embeds2, p=2)
	pckEmbeds1 = embeds1[nodes]
	pckEmbeds2 = embeds2[nodes]
	nume = torch.exp(torch.sum(pckEmbeds1 * pckEmbeds2, dim=-1) / temp)
	deno = torch.exp(pckEmbeds1 @ embeds2.T / temp).sum(-1)
	return -torch.log(nume / deno).mean()