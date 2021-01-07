import argparse
import logging
import time
import cv2
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from tf_pose.estimator import TfPoseEstimator
from tf_pose.networks import get_graph_path, model_wh

logger = logging.getLogger('TfPoseEstimator-Video')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

fps_time = 0

body = ["Nos", "Nec", "Rsh", "Rel", "Rwr", "Lsh", "Lel", "Lwr", "Rhi", "Rkn", "Ran", "Lhi", "Lkn", "Lan", "Rey", "Ley", "Rea", "Lea"]
column_name = ["Nos_X","Nos_Y","Nos_Score","Nec_X", "Nec_Y", "Nec_Score", "Rsh_X","Rsh_Y", "Rsh_Score","Rel_X","Rel_Y","Rel_Score",
"Rwr_X","Rwr_Y","Rwr_Score","Lsh_X","Lsh_Y","Lsh_Score","Lel_X","Lel_Y","Lel_Score", "Lwr_X","Lwr_Y","Lwr_Score","Rhi_X","Rhi_Y","Rhi_Score","Rkn_X","Rkn_Y","Rkn_Score",
"Ran_X","Ran_Y","Ran_Score","Lhi_X","Lhi_Y","Lhi_Score","Lkn_X","Lkn_Y","Lkn_Score", "Lan_X","Lan_Y","Lan_Score","Rey_X","Rey_Y","Rey_Score","Ley_X","Ley_Y","Ley_Score",
"Rea_X","Rea_Y","Rea_Score","Lea_X","Lea_Y","Lea_Score"]
data = []

parser = argparse.ArgumentParser(description='tf-pose-estimation Video')
parser.add_argument('--video', type=str, default='')
parser.add_argument('--resolution', type=str, default='432x368', help='network input resolution. default=432x368')
parser.add_argument('--model', type=str, default='mobilenet_thin', help='cmu / mobilenet_thin / mobilenet_v2_large / mobilenet_v2_small')
parser.add_argument('--show-process', type=bool, default=False, help='for debug purpose, if enabled, speed for inference is dropped.')
parser.add_argument('--showBG', type=bool, default=True, help='False to show skeleton only.')
parser.add_argument('--savefile', type=str, required=True, help='저장할 파일 이름')
args = parser.parse_args()
logger.debug('initialization %s : %s' % (args.model, get_graph_path(args.model)))
w, h = model_wh(args.resolution)
e = TfPoseEstimator(get_graph_path(args.model), target_size=(w, h))
cap = cv2.VideoCapture("/home/educon/data2/video/"+args.video)
if cap.isOpened() is False:
    print("Error opening video stream or file")
while cap.isOpened():
    tmp = [[] for _ in range(18*3)]
    ret_val, image = cap.read()

    if ret_val:
        humans = e.inference(image, upsample_size=4.0)
        if humans:
            #save data generated by tfpose
            for i in range(0,18):
                if i not in humans[0].body_parts.keys():
                    tmp[3*i] = 0
                    tmp[3*i+1] = 0
                    tmp[3*i+2] = 0
                else:
                    #detect human
                    tmp[3*i] = humans[0].body_parts[i].x
                    tmp[3*i+1] = humans[0].body_parts[i].y
                    tmp[3*i+2] = humans[0].body_parts[i].score
            data.append(tmp)
        
        if not args.showBG:
            image = np.zeros(image.shape)
        image = TfPoseEstimator.draw_humans(image, humans, imgcopy=False)
        
        #show image
        cv2.putText(image, "FPS: %f" % (1.0 / (time.time() - fps_time)), (10, 10),  cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        cv2.imshow('tf-pose-estimation result', image)
        
        fps_time = time.time()
        if cv2.waitKey(1) == 27:
            break
    else:
        break
cv2.destroyAllWindows()

#build dataframe to save pickle
init_data = pd.DataFrame(data=data, columns=column_name)
init_data.to_pickle("/home/educon/Desktop/tfpose/hci_tfpose/data_pickle/"+args.savefile+".pkl")
logger.debug('finished+')