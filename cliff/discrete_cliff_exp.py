import sys
sys.path.append('.')

import ccm
ccm.run('cliff/discrete_cliff',10, goal_reward=[-1, 0, 1, 10, 100])
