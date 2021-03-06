import h5py as h
import cvxpy as C
import numpy as np
from matplotlib import pyplot as plt
from argparse import ArgumentParser as AP

p = AP()
p.add_argument('--C1', required=True, type=float, help='C1 parameter')
p.add_argument('--C2', required=True, type=float, help='C2 parameter')
opt = p.parse_args()

# Load the dataset
f = h.File('toy.hdf5', 'r')
X = np.array(list(f['X'])).T
y = np.array(list(f['y'])).T
print('Dataset loaded: X.shape = {0}'.format(X.shape))

# Declare the variables to optimize over
m, d = X.shape[0], X.shape[1]
beta = C.Variable(d)
beta_0 = C.Variable(1)
slackvar = C.Variable(m)

# Declare the objective function
objective = (C.sum_squares(beta))*0.5
for i in range(0, m):
    if y[i] == 1:
        objective += slackvar[i]*opt.C1
    else:
        objective += slackvar[i]*opt.C2

# Declare the constraints to enforce
constraints = [slackvar >= 0]
for i in range(0, m):
    constraints += [y[i]*(beta.T*X[i] + beta_0) >= 1 - slackvar[i]]

# Define the problem
problem = C.Problem(C.Minimize(objective), constraints)

# Solve the problem
problem.solve(solver=C.ECOS, abstol=1e-10, reltol=1e-09, feastol=1e-10, max_iters=1000)

print("Problem exited with status: {0} and value attained: {1}".format(problem.status, round(problem.value, 5)))

# Saving the y(<beta, x> + beta_0) into a text file
beta_file = open('beta.txt', 'w')

# Plotting section
plt.ylabel('$x_{1}$', fontsize=20)
plt.xlabel('$x_{2}$', fontsize=20)
truths = [False, False, False]
for i in range(0, m):
    beta_file.write('{0}\n'.format(round(y[i]*(np.dot(np.array(beta.value).reshape(-1), X[i]) + beta_0.value), 8)))
    if y[i] == 1:
        point_type = 'mo' if (slackvar[i].value) > 1e-06 else 'go'

        if point_type == 'go' and truths[0] == False:
            plt.plot(X[i,0], X[i,1], point_type, label='+1')
            truths[0] = True
        elif point_type == 'mo' and truths[2] == False:
            plt.plot(X[i,0], X[i,1], point_type, label='$\\xi_{i} > 0$')
            truths[2] = True
        else:
            plt.plot(X[i,0], X[i,1], point_type)
    else:
        point_type = 'mo' if (slackvar[i].value) > 1e-06 else 'bo'

        if point_type == 'bo' and truths[1] == False:
            plt.plot(X[i,0], X[i,1], point_type, label='-1')
            truths[1] = True
        elif point_type == 'mo' and truths[2] == False:
            plt.plot(X[i,0], X[i,1], point_type, label='$\\xi_{i} > 0$')
            truths[2] = True
        else:
            plt.plot(X[i,0], X[i,1], point_type)

x = np.arange(np.amin(X[:,0]), np.amax(X[:,0]), 0.001)
beta = np.array(beta.value).reshape(-1).tolist()
beta_0 = beta_0.value
y_decbound = -beta_0/beta[1] - beta[0]*x/beta[1]
plt.plot(x, y_decbound, 'k-', label='Decision Boundary')

y_margin1 = (1 - beta_0 - beta[0]*x)/beta[1]
plt.plot(x, y_margin1, 'r--')
y_margin2 = (-1 - beta_0 - beta[0]*x)/beta[1]
plt.plot(x, y_margin2, 'r--', label='Support Vectors')

print("Margin width: {0}".format(2/np.sqrt(beta[0]**2 + beta[1]**2)))

plt.legend(loc='upper right', numpoints=1, ncol=2)
plt.show()

# Calculating prediction error
total_error = 0
for i in range(0, m):
    pred = np.sign((np.dot(beta, X[i]) + beta_0))
    if pred == 1 and y[i] == -1:
        total_error += opt.C2
    elif pred == -1 and y[i] == 1:
        total_error += opt.C1
print("Total Weighted Classification Error for C1 = {0} and C2 = {1} is {2}".format(opt.C1, opt.C2, total_error))
