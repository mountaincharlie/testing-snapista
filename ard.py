# just try processing one of the UK scenes to calibrated and compare to snap process
# recreate todays process?
# recreate a non-AM fiji scene as catapult did

from snapista import Operator, OperatorParams
# from snapista import Graph
# from snapista import TargetBand, TargetBandDescriptors

# Graph.list_operators()
# Graph.describe_operators() 

calibration = Operator('Calibration')
# calibration.describe()
calibration.createBetaBand = 'false'
