import numpy as np
from abstractbm import AbstractBM

__license__ = 'MIT License <http://www.opensource.org/licenses/mit-license.php>'
__author__ = 'Lucas Theis <lucas@tuebingen.mpg.de>'
__docformat__ = 'epytext'

class GaussianRBM(AbstractBM):
	"""
	An implementation of the Gaussian RBM with continuous visible nodes.

	References:
	Salakhutdinov, R. (2009). I{Learning Deep Generative Models.}

	@type sigma: real
	@ivar sigma: controls the variance of conditional distribution of the 
	visible units
	"""

	def __init__(self, num_visibles, num_hiddens):
		AbstractBM.__init__(self, num_visibles, num_hiddens)

		# hyperparameters
		self.sigma = 0.2
		self.vsigma = np.asmatrix(np.ones(num_visibles)).T
		self.dvsigma = np.ones_like(self.vsigma)
		#print max(self.vsigma),max(self.dvsigma)


	def forward(self, X=None):
		if X is None:
			X = self.X
		else:
			X = np.asmatrix(X)
	#	print self.W.T.shape,X.shape
		#self.Q = 1. / (1. + np.exp(-self.W.T * X ))#/ self.sigma - self.c))
		self.Q = 1. / (1. + np.exp(-self.W.T * (X/np.square(self.vsigma)) - self.c))
		self.Y = (np.random.rand(*self.Q.shape) < self.Q).astype(self.Q.dtype)
		return self.Y.copy()



	def backward(self, Y=None, X=None):
		if Y is None:
			Y = self.Y
		else:
			Y = np.asmatrix(Y)
		
		#self.X = (self.sigma * self.W * Y + self.b + self.sigma * np.random.randn(self.X.shape[0], Y.shape[1]))
		self.X = (np.multiply(self.vsigma,self.W * Y + self.b )) #+ np.multiply(self.vsigma,np.random.randn(self.X.shape[0], Y.shape[1])))
		return self.X.copy()



	def _ulogprob(self, X, Y, all_pairs=False):
		X = np.asmatrix(X)
		Y = np.asmatrix(Y)

		if all_pairs:
			return -np.sum(np.square(X - self.b), 0).T / (2. * self.sigma * self.sigma) \
					+ X.T * self.W * Y / self.sigma \
					+ self.c.T * Y
		else:
			return -np.sum(np.square(X - self.b), 0) / (2. * self.sigma * self.sigma) \
					+ np.sum(np.multiply(X, self.W * Y), 0) / self.sigma \
					+ self.c.T * Y



	def _ulogprob_vis(self, X):
		X = np.asmatrix(X)

		return -np.sum(np.square(X - self.b), 0) / (2. * self.sigma * self.sigma) \
				+ np.sum(np.log(1. + np.exp(self.W.T * X / self.sigma + self.c)), 0)



	def _ulogprob_hid(self, Y):
		Y = np.asmatrix(Y)

		v = pow(self.sigma, 2)
		d = self.X.shape[0]
		c = np.sum(np.square(self.W * Y * self.sigma + self.b), 0) / v
		b = self.b.T * self.b / v
		a = self.c.T * Y

		return a - b / 2. + c / 2. + d / 2. * np.log(2 * np.pi) + d * np.log(self.sigma)



	def _train_sleep(self, X, Y):
		X = np.asmatrix(X)
		Y = np.asmatrix(Y)

		Q = 1. / (1. + np.exp(-self.W.T * X / self.sigma - self.c))

		tmp1 = np.multiply(Y, 1 - Q)
		tmp2 = np.multiply(Y - 1, Q)

		self.dW = X * (tmp1 + tmp2).T / X.shape[1] + self.momentum * self.dW
		self.dc = tmp1.mean(1) + tmp2.mean(1) + self.momentum * self.dc

		self.W += self.dW * self.learning_rate
		self.c += self.dc * self.learning_rate



	def _train_wake(self, X, Y):
		X = np.asmatrix(X)
		Y = np.asmatrix(Y)

		tmp = X - self.sigma * self.W * Y - self.b
		self.dW = tmp * Y.T / X.shape[1] + self.momentum * self.dW
		self.db = tmp.mean(1) + self.momentum * self.db

		self.W += self.dW * self.learning_rate
		self.b += self.db * self.learning_rate



	def _clogprob_hid_vis(self, X, Y, all_pairs=False):
		X = np.asmatrix(X)
		Y = np.asmatrix(Y)

		Q = 1. / (1. + np.exp(-self.W.T * X / self.sigma - self.c))

		if all_pairs:
			P = 1. - Q
			P[P == 0] = 1E-320
			Q[Q == 0] = 1E-320

			return np.log(Q).T * Y + np.log(P).T * (1. - Y)
		else:
			return np.sum(np.log(2 * np.multiply(Q, Y) - Y - (Q - 1)), 0)



	def _clogprob_vis_hid(self, X, Y, all_pairs=False):
		X = np.asmatrix(X)
		Y = np.asmatrix(Y)

		S = self.W * Y * self.sigma + self.b

		if all_pairs:
			return -(np.sum(np.square(X), 0).T - 2. * X.T * S + np.sum(np.square(S), 0)) / (2. * self.sigma * self.sigma) \
					- X.shape[0] * np.log(np.sqrt(2. * np.pi) * self.sigma)
		else:
			return -np.sum(np.square(X - S), 0) / (2. * self.sigma * self.sigma) \
					- X.shape[0] * np.log(np.sqrt(2. * np.pi) * self.sigma)



	def _free_energy_gradient(self, X):
		Q = 1. / (1. + np.exp(-self.W.T * X / self.sigma - self.c))
		return (X - self.b) / (self.sigma * self.sigma) - self.W * Q



	def _centropy_hid_vis(self, X):
		# compute conditional probabilities of hidden units being active
		Q = 1. / (1. + np.exp(-self.W.T * np.asmatrix(X) / self.sigma - self.c))

		A = np.multiply(Q, np.log(Q))
		B = np.multiply(1. - Q, np.log(1. - Q))

		# zero times infinity gives zero
		A[Q == 0] = 0
		B[Q == 1] = 0

		# integrate
		return -np.sum(A + B, 0)

	def train(self, X):
		"""
		Trains the parameters of the BM on a batch of data samples. The
		data stored in C{X} is used to estimate the likelihood gradient and
		one step of gradient ascend is performed.

		@type  X: array_like
		@param X: example states of the visible units
		"""
		#print "I am traing sigma"
		X = np.asmatrix(X)
		Xtemp = X.copy()
		#print "X shape", X.shape
		# positive phase
		Y = self.forward(X)
		Ytemp = Y.copy()
		# store posterior probabilities
		Q = self.Q.copy()
		pos = X*Y.T
		posSigma = np.square(Xtemp - self.b)/np.power(self.vsigma,3) - np.multiply(self.W*Ytemp,Xtemp)/np.square(self.vsigma)
		
		if self.persistent:
			self.X = self.pX
			self.Y = self.pY

		# negative phase
		for t in range(self.cd_steps):
			#print 'cd', t
			X = self.backward(Y)
			Y = self.forward(X)

		if self.persistent:
			self.pX = self.X.copy()
			self.pY = self.Y.copy()
		#print max(X),max(self.b)
		negSigma = np.square(X - self.b)/np.power(self.vsigma,3) - np.multiply(self.W*Y,X)/np.square(self.vsigma)
		# update parameters
		self.dW = pos / X.shape[1] - self.X * self.Q.T / self.X.shape[1] \
		        - self.weight_decay * self.W \
		        + self.momentum * self.dW
		self.dvsigma = posSigma - negSigma #- self.weight_decay*self.vsigma + self.momentum*self.dvsigma
		#print "sigma Gradient: ", self.dvsigma
		self.db = Xtemp.mean(1) - self.X.mean(1) + self.momentum * self.db
		self.dc = Q.mean(1) - self.Q.mean(1) + self.momentum * self.dc
#		        - self.sparseness * np.multiply(np.multiply(Q, 1. - Q).mean(1), (Q.mean(1) - self.sparseness_target))

		self.W += self.dW * self.learning_rate
		self.vsigma += self.dvsigma * 0.0001
		self.b += self.db * self.learning_rate
		self.c += self.dc * self.learning_rate