import cv2
import numpy as np
from sklearn.cluster import KMeans
from sklearn import svm
from sklearn.model_selection import train_test_split
from sklearn.externals import joblib

SIFTfeatures=[]
numEachPic=[]
# from matplotlib import pyplot as plt
#sift
def siftExtrator(poseName,poseId):
	print(poseName)
	featuresEveryPic=[]
	for i in range(10):
		img=cv2.imread('./hand-reader-dataset/%c/0%d00%d.jpg'%(poseName,poseId,i))
		# print('./hand-reader-dataset/%c/0000%d.jpg'%(poseId,i))
		img=cv2.resize(img,(180,120))
		gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
		sift=cv2.xfeatures2d.SIFT_create()
		kp,des=sift.detectAndCompute(gray,None)
		des=des.T/des.sum(axis=1,dtype='float')
		# print('this descriptor shape:',des.shape)
		if i==0:
			descriptors=des
			ret,thresh=cv2.threshold(gray,25,255,cv2.THRESH_BINARY)
			cv2.imwrite('template%d.jpg'%poseId,img)
		else:
			descriptors=np.concatenate((descriptors,des),axis=1)
		# print('all descriptors shape:',descriptors.shape)
		featuresEveryPic.append(des.shape[1])
		img=cv2.drawKeypoints(gray,kp,None,flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
		cv2.imwrite('./test/sift%c%d.jpg'%(poseName,i),img)
	for i in range(11,50):
		img=cv2.imread('./hand-reader-dataset/%c/0%d0%d.jpg'%(poseName,poseId,i))
		# print('./hand-reader-dataset/%c/000%d.jpg'%(poseId,i))
		img=cv2.resize(img,(180,120))
		gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
		sift=cv2.xfeatures2d.SIFT_create()
		kp,des=sift.detectAndCompute(gray,None)
		des=des.T/des.sum(axis=1,dtype='float')
		descriptors=np.concatenate((descriptors,des),axis=1)
		featuresEveryPic.append(des.shape[1])
		img=cv2.drawKeypoints(gray,kp,None,flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
		cv2.imwrite('./test/sift%c%d.jpg'%(poseName,i),img)
	print(descriptors.shape)
	return descriptors, featuresEveryPic

def Kmeans(descriptor,num_clusters):
	descriptor = np.float32(descriptor)
	# Define criteria = ( type, max_iter = 10 , epsilon = 1.0 )
	criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
	# Set flags use kmeans++ initialization
	flags = cv2.KMEANS_PP_CENTERS
	# Apply KMeans
	compactness,labels,centers = cv2.kmeans(descriptor,num_clusters,None,criteria,10,flags)
	# compactness gives the error, labels gives the cluster each point is in
	# centers gives the value of center
	# NumberOfNodes = np.array([list(labels).count(i) for i in range(50) ])
	# NumberOfNodes gives number of nodes in each cluster.
	# print(compactness)
	# return NumberOfNodes
	return labels,centers

def kmeansNew(descriptor,num_clusters):
	kmeans=KMeans(n_clusters=num_clusters, random_state=0).fit(descriptor)
	return kmeans

def featureMap(pointer,poseName,poseId):
	global SIFTfeatures,numEachPic
	Descriptor,featuresEveryPic = siftExtrator(poseName,poseId)
	SIFTfeatures.append(Descriptor)
	pointer+=sum(featuresEveryPic)
	numEachPic.append(featuresEveryPic)
	return pointer

def readInAndMatch():
	pointer=0
	FeatureOfPose={}
	for i in range(4):
		FeatureOfPose[chr(ord('A')+i)]=featureMap(pointer,chr(ord('A')+i),i)
		pointer=FeatureOfPose[chr(ord('A')+i)]
	# FeatureOfPose['G']=featureMap(pointer,'G',4)
	# pointer=FeatureOfPose['G']
	FeatureOfPose['H']=featureMap(pointer,'H',5)
	pointer=FeatureOfPose['H']
	FeatureOfPose['I']=featureMap(pointer,'I',6)
	pointer=FeatureOfPose['I']
	FeatureOfPose['L']=featureMap(pointer,'L',7)
	pointer=FeatureOfPose['L']
	FeatureOfPose['V']=featureMap(pointer,'V',8)
	pointer=FeatureOfPose['V']
	FeatureOfPose['Y']=featureMap(pointer,'Y',9)
	pointer=FeatureOfPose['Y']
	allFeatures=np.concatenate(tuple(SIFTfeatures),axis=1)
	return FeatureOfPose,allFeatures

def BoWeveryPic(numEachPic,labels):
	ptr=0
	poseId=0
	dictPose={}
	for pose in numEachPic:
		BoWOfPose=[]
		for pic in pose:
			BowVectors=np.zeros((1,210),dtype=int)
			unique,counts=np.unique(labels[ptr:ptr+pic],return_counts=True)
			index=np.array(range(counts.shape[0]))
			BowVectors[0,unique]=counts[index]
			BoWOfPose.append(BowVectors)
			ptr+=pic
		dictPose[poseId]=BoWOfPose
		poseId+=1
	return dictPose


FeatureOfPose,allFeatures=readInAndMatch()
print('size:',allFeatures.shape)
kmeans=kmeansNew(allFeatures.T,210)
joblib.dump(kmeans,"./mode/kmeans.pkl")
Words=kmeans.cluster_centers_
labels=kmeans.labels_
# print(labels.size)
# print(Words[1])
dictPose=BoWeveryPic(numEachPic,labels)
# print(dictPose)
lb = np.array([])
test_set = []
for ts in range(9):
	lb = np.concatenate([lb,np.linspace(ts,ts,len(dictPose[ts]))])
	for d in range(len(dictPose[ts])):
		test_set.append(list(dictPose[ts][d][0]))
# print(lb)
# print(test_set)
# split the testdata and training data
# x_train, x_test, y_train, y_test = train_test_split(test_set,lb,random_state=1,train_size=0.9)
# print('test_set ',test_set)
# print('lb ',lb)

# print('x_train ',x_train)
# print('y_train ',y_train)
# print('x_test ',x_test)
# print('y_test ',y_test)

# clf = svm.SVC( kernel='rbf', gamma=20, decision_function_shape='ovr')
clf = svm.SVC( kernel='linear', decision_function_shape='ovr')
# clf.fit(x_train, y_train.ravel())
clf.fit(test_set, lb.ravel())
# print (clf.score(x_train, y_train) )
# y_hat = clf.predict(x_train)
# print (clf.score(x_test, y_test))
# y_hat = clf.predict(x_test)
# print ('decision_function:\n', clf.decision_function(x_train))
# print ('\npredict:\n', clf.predict(x1))
# print ('\npredict:\n', clf.predict(x_test))
joblib.dump(clf,"./mode/svm.m")
