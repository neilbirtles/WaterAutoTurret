#ifndef __INCLUDE_DETECT_API_H_
#define __INCLUDE_DETECT_API_H_

#ifdef __cplusplus
extern "C"{
#endif

#include "detect_common.h"

#define _CHECK__STATUS_(stat, lbl) do {\
	if (stat) {\
		printf("%s CHECK STATUS %d\n", __FUNCTION__, __LINE__);\
		goto lbl;\
	}\
}while(0)

det_status_t det_set_model(det_model_type modelType);     ///<set network type,this will trigger init process
det_status_t det_get_model_size(det_model_type modelType, int *width, int *height, int *channel);
det_status_t det_set_input(input_image_t imageData, det_model_type modelType);      ///<set input image to network
det_status_t det_get_result(pDetResult resultData, det_model_type modelType);       ///<get detection result,this will block until process end
det_status_t det_release_model(det_model_type modelType);       ///<get detection result,this will block until process end
det_status_t det_set_log_config(det_debug_level_t level,det_log_format_t output_format);  ///<set log config

#ifdef __cplusplus
}
#endif

#endif
