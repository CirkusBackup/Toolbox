import sys, os
import imageio
import numpy
from PIL import Image

def framePadding(frame,padding):
	frame = int(float(frame)) #convert to int
	fullFrame = '%0*d'%(padding,frame) #add padding
	return fullFrame

def convert_exr_to_jpg(exr_frame):
	#imageio.plugins.freeimage.download() #DOWNLOAD IT
	image = imageio.imread(exr_frame)
	#print(image.dtype)
	image = image[:,:,:3] #remove alpha channel
	im_gamma_correct = numpy.clip(numpy.power(image, 0.45), 0, 1) #gamma correction
	im_fixed = Image.fromarray(numpy.uint8(im_gamma_correct*255)) #gamma correction
	return im_fixed 

def layoutFrames(exr_file, jpg_file,frames):

	#exr_file = "/media/bigtop/Job_2/Z Pumped People/Elements/3D_RENDERS/RENDER/Bespoke/noMinimumSpend/SH0010/ravi/SH0010_noMinSpend_v002_cl/SH0010_ravi"
	#jpg_file = "/media/bigtop/Job_2/Z Pumped People/Elements/3D_RENDERS/RENDER/Bespoke/noMinimumSpend/SH0010/ravi/SH0010_noMinSpend_v002_cl/SH0010_ravi_tn.png"

	#frames = [1]
	#frames = [30,40,50,60,70,80,90,100]
	background = '' #holding string for background image
	r=0 #first row index
	newsize = (256,256) #holding tuple for image size
	for i,f in enumerate(frames):
		c = i - r*3 #calculate column index

		exr_frame = "%s.%s.exr"%(exr_file,framePadding(f,4)) #file name
		if not os.path.isfile(exr_frame):
			return False

		filename, extension = os.path.splitext(exr_frame)
		if not extension.lower().endswith('.exr'):
			return False

		im_fixed = convert_exr_to_jpg(exr_frame) #convert .exr to PIL image
		
		if i == 0: #only do once
			img_w, img_h = im_fixed.size #get image size
			scaleAmount = img_w/256 #get the amount img width is resized
			newsize = (256, int(img_h/scaleAmount)) #img height should be resized
		im_fixed = im_fixed.resize(newsize) #do resize
		if background == '': #check if background image already exists
			background = Image.new('RGBA',(newsize[0], newsize[1]), (255, 0, 0, 255)) #make background image
		else:
			bg_w, bg_h = background.size #get existing background size
			width = bg_w+c*newsize[0] #calculate new width
			if width > 3*newsize[0]: #compare width the column limit
				width = 3*newsize[0] #make sure the width does excede the column limit
			background = background.crop((0,0,width,newsize[1]+r*newsize[1])) #resize background to fit another thumbnail
		offset = (c*newsize[0],r*newsize[1]) #position thumbnail on background
		background.paste(im_fixed,offset) #paste thumbnail onto background 

		if c == 2: #last column index
			r += 1 #increment row index

	background.save(jpg_file) #save the file as .jpg

if __name__ == '__main__':
	exr = "pose_Aaron"
	jpg = "pose_Aaron_tn.png"
	layoutFrames(exr, jpg,[109])