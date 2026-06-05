import joblib
import numpy as np

scaler = joblib.load("arduino_inference/scaler.pkl")

def fmt(arr):
    return ",\n".join(f"    {v:.8f}f" for v in arr)

print(f"""#ifndef SCALER_PARAMS_H
#define SCALER_PARAMS_H

const float scaler_mean[28] = {{
{fmt(scaler.mean_)}
}};

const float scaler_scale[28] = {{
{fmt(scaler.scale_)}
}};

#endif""")
