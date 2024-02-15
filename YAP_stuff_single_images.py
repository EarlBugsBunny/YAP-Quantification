import os
import pandas as pd
import numpy as np
import imageio
from skimage.filters import threshold_otsu
from scipy.ndimage import gaussian_filter
from skimage import morphology
from skimage import filters



def thresholding(stack):
    flattend = stack.flatten()
    threshold = threshold_otsu(flattend)
    return threshold


def create_thresholded_images(stack):
    treshold = thresholding(stack)
    
    thresholded_stack = np.zeros_like(stack)
    #sigma = 1
    for i in range(stack.shape[0]):
        thresholded_stack[i] = np.where(stack[i] > treshold, 255, 0)
        #thresholded_stack[i] = gaussian_filter(thresholded_stack[i], sigma=sigma)
        #thresholded_stack[i] = morphology.remove_small_objects(thresholded_stack[i], min_size=500)
        thresholded_stack[i] = filters.median(thresholded_stack[i])
        thresholded_stack[i] = filters.median(thresholded_stack[i])
        thresholded_stack[i] = filters.median(thresholded_stack[i])
        #thresholded_stack[i] = morphology.remove_small_objects(thresholded_stack[i], min_size=500)
        
    return thresholded_stack
    
 
def open_file(folder_path,channel):
    for filename in os.listdir(folder_path):
        channel_name = "C="+str(channel)
        if filename.endswith(".tif") and channel_name in filename:
            file_path = os.path.join(folder_path, filename)
            image = imageio.volread(file_path)
            return image, file_path
    return None

def get_thresholed_image(stack, file_path):
    thresholded_stack = create_thresholded_images(stack)  
    output_path = file_path + "_thresholded.tif"
    imageio.volsave(output_path, thresholded_stack)
    return thresholded_stack

def get_intensity(yap_stack, condition_stack):
    all_images_cond = np.empty(1)
    for i in range(yap_stack.shape[0]):
        yap_intensity_condition = yap_stack[i][condition_stack[i] == 255]
        all_images_cond = np.concatenate((all_images_cond, yap_intensity_condition))
    all_images_cond = all_images_cond[1:]
    mean_intensity = np.mean(all_images_cond)
    median_intensity = np.median(all_images_cond)
    return mean_intensity, median_intensity

def get_ratios(folder_path):
    actin_stack, actin_file_path = open_file(folder_path,3)
    actin_threshold = get_thresholed_image(actin_stack, actin_file_path)

    dapi_stack, dapi_file_path = open_file(folder_path,2)
    dapi_threshold = get_thresholed_image(dapi_stack, dapi_file_path)

    yap_stack, yap_file_path = open_file(folder_path,0)
    
    mean_actin, median_actin = get_intensity(yap_stack, actin_threshold)
    mean_dapi, median_dapi = get_intensity(yap_stack, dapi_threshold)


    # Add a row to the DataFrame with values
    new_row_values = {
        "filename": folder_path,
        "mean_at_actin": mean_actin,
        "median_at_actin": median_actin,
        "mean_at_dapi": mean_dapi,
        "median_at_dapi": median_dapi,
        "ratio_mean_yap_over_actin": mean_dapi/mean_actin,
        "ratio_median_yap_over_actin": median_dapi/median_actin
    }
    
    return new_row_values
    
    
# Create an empty DataFrame with columns and initial values
columns = ["filename", "mean_at_actin", "median_at_actin", "mean_at_dapi", "median_at_dapi", "ratio_mean_yap_over_actin", "ratio_median_yap_over_actin"]
initial_values = {"filename": [], "mean_at_actin": [], "median_at_actin": [],
                  "mean_at_dapi": [], "median_at_dapi": [], "ratio_mean_yap_over_actin": [], "ratio_median_yap_over_actin": []}

df_overall = pd.DataFrame(initial_values, columns=columns)



current_directory = os.getcwd()
for folder_path in os.listdir(current_directory):
    print(folder_path)
    values = get_ratios(folder_path)
    df_overall = pd.concat([df_overall, pd.DataFrame([values])], ignore_index=True)
    

output_csv_path = os.path.join(os.getcwd(), 'output.xlsx')
df_overall.to_excel(output_csv_path)
    







    
    
















