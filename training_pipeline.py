import os
import numpy as np
import pandas as pd
import yfinance as yf
import datetime
import shutil
import plotly.express as px
from subprocess import run


keys_selected_index = ["^XAX", '^GSPC', '^DJI', '^IXIC', '^NYA', '^FCHI', '^RUT', '^FTSE', "^VIX", "^GDAXI"]

selected_index = {'^FCHI': "CAC 40", '^GSPC': "S&P 500", '^DJI': "Jones Industrial Average",
                  '^IXIC': "NASDAQ Composite", '^NYA': "NYSE COMPOSITE (DJ)", "^XAX": "NYSE AMEX COMPOSITE",
                  '^RUT': "Russell 2000", '^FTSE': "FTSE 100", "^VIX": "CBOE Volatility Index",
                  "^GDAXI": "DAX PERFORMANCE-INDEX"}

projections = [1, 15, 28, 44, 66, 131, 262]

def MSE(pred, true):
    return np.mean((pred - true) ** 2)
def MAE(pred, true):
    return np.mean(np.abs(pred - true))
def RSE(pred, true):
    return np.sqrt(np.sum((true - pred) ** 2)) / np.sqrt(np.sum((true - true.mean()) ** 2))



def load_fresh_data(keys_selected_index=keys_selected_index, column_target = "Close", columns_to_drop = [], df_date_min = "2010-01-01", pipeline_path=""):
    tickers = yf.Tickers(" ".join(keys_selected_index))
    index_info = {}
    columns = ["Open", "High", "Low", "Close", "Volume"]
    for sym in keys_selected_index:
        tmp = tickers.tickers[sym].history(period="max")
        tmp.index = tmp.index.tz_convert(None)
        tmp.index = tmp.index.date
        index_info[sym] = tmp[columns]

    for key in keys_selected_index:
        df = index_info[key]
        try:
            df.index = df.index.tz_convert(None)
            idf.index = df.index.date
        except:
            pass
        df = df.drop(columns=columns_to_drop)
        df = df.rename(columns={column_target: 'OT'})
        date_to_filter = [index_date for index_date in df.index if
                          index_date >= datetime.date.fromisoformat(df_date_min)]
        tmp = df.filter(items=date_to_filter, axis=0).copy()
        tmp.index.name = 'date'
        tmp.to_csv(f"{pipeline_path}pythonProject/dataset/custom_dataset_{key}.csv")


def start_training(key, seq_len=30, pred_len=60, dm=256, target_type="MS", df=128, el=4, nh=32, ll=0, pipeline_path=""):
    model_name = "PatchTST"
    root_path_name = "./dataset/"
    data_path_name = f"custom_dataset_{key}.csv"
    model_id_name = f"test_custom_{key}"
    data_name = "custom"
    random_seed = 2021
    result_folder_path = f"{pipeline_path}data/current/data_{key}"
    result_archive_path = f"{pipeline_path}data/archive/data_{key}"

    for directory in ["pred", "true", "x", "training_log", 'real_prediction']:
        if not os.path.exists(f"{result_folder_path}/{directory}"):
            os.makedirs(f"{result_folder_path}/{directory}")

    for directory in ["pred", "true", "x", "log", 'real_prediction']:
        if not os.path.exists(f"{result_archive_path}/{directory}"):
            os.makedirs(f"{result_archive_path}/{directory}")

    script = f"""python run_longExp.py --random_seed {random_seed} --is_training 1 --root_path {root_path_name}""" \
             f""" --data_path {data_path_name} --model_id {model_id_name}_{seq_len}_{pred_len} --model {model_name}""" \
             f""" --data {data_name} --features {target_type} --seq_len {seq_len} --pred_len {pred_len} --enc_in 5""" \
             f""" --freq d --label_len {ll} --e_layers {el} --n_heads {nh} --use_gpu true --batch_size 16""" \
             f""" --d_model {dm} --d_ff {df} --dropout 0.2 --fc_dropout 0 --head_dropout 0.1 --patch_len 32 """ \
             f""" --stride 2 --des 'Exp'  --train_epochs 100 --patience 5 --lradj 'TST' --pct_start 0.2 --itr 1 """ \
             f""" --learning_rate 0.0001 --do_predict """ \
             f""">logs/LongForecasting/{model_name}_{model_id_name}_{seq_len}_{pred_len}.log"""

    run(script, cwd=f"{pipeline_path}pythonProject", shell=True)

    pred = np.load(
        f"{pipeline_path}pythonProject/results/test_custom_{key}_{seq_len}_{pred_len}_PatchTST_custom_ft{target_type}_sl{seq_len}_ll{ll}_pl{pred_len}_dm{dm}_nh{nh}_el{el}_dl1_df{df}_fc1_ebtimeF_dtTrue_Exp_0/pred.npy")

    true = np.load(
        f"{pipeline_path}pythonProject/results/test_custom_{key}_{seq_len}_{pred_len}_PatchTST_custom_ft{target_type}_sl{seq_len}_ll{ll}_pl{pred_len}_dm{dm}_nh{nh}_el{el}_dl1_df{df}_fc1_ebtimeF_dtTrue_Exp_0/true.npy")
    x = np.load(
        f"{pipeline_path}pythonProject/results/test_custom_{key}_{seq_len}_{pred_len}_PatchTST_custom_ft{target_type}_sl{seq_len}_ll{ll}_pl{pred_len}_dm{dm}_nh{nh}_el{el}_dl1_df{df}_fc1_ebtimeF_dtTrue_Exp_0/x.npy")
    real_prediction = np.load(
        f"{pipeline_path}pythonProject/results/test_custom_{key}_{seq_len}_{pred_len}_PatchTST_custom_ft{target_type}_sl{seq_len}_ll{ll}_pl{pred_len}_dm{dm}_nh{nh}_el{el}_dl1_df{df}_fc1_ebtimeF_dtTrue_Exp_0/real_prediction.npy")

    src = f"{pipeline_path}pythonProject/logs/LongForecasting/{model_name}_{model_id_name}_{seq_len}_{pred_len}.log"
    dst = f"{result_folder_path}/training_log/j+{pred_len}.log"

    shutil.copyfile(src, dst)
    np.save(f"{result_folder_path}/pred/j+{pred_len}.npy", pred)
    np.save(f"{result_folder_path}/true/j+{pred_len}.npy", true)
    np.save(f"{result_folder_path}/x/j+{pred_len}.npy", x)
    np.save(f"{result_folder_path}/real_prediction/j+{pred_len}.npy", real_prediction)

    dst = f"{result_archive_path}/log/{datetime.date.today()}_j+{pred_len}.log"

    shutil.copyfile(src, dst)

    np.save(f"{result_archive_path}/pred/{datetime.date.today()}_j+{pred_len}.npy", pred)
    np.save(f"{result_archive_path}/true/{datetime.date.today()}_j+{pred_len}.npy", true)
    np.save(f"{result_archive_path}/x/{datetime.date.today()}_j+{pred_len}.npy", x)
    np.save(f"{result_archive_path}/real_prediction/{datetime.date.today()}_j+{pred_len}.npy", real_prediction)



def import_training_result(key, pred_lens, pipeline_path="", target_path="../project_chef_d_oeurvre/"):
    result_folder_path = f"{pipeline_path}data/current/data_{key}"
    data_app = f"{pipeline_path}data/app/close_{key}"
    dataset = pd.read_csv(f"{pipeline_path}pythonProject/dataset/custom_dataset_{key}.csv", index_col="date")['OT']
    start_time = datetime.date.fromisoformat(dataset.index.max()) + datetime.timedelta(days=1)

    pred_len = pred_lens[-1]
    new_date_index = pd.date_range(start_time, start_time + datetime.timedelta(days=pred_len // 5 * 7), freq='B')
    if len(new_date_index) > pred_len:
        new_date_index = new_date_index[:pred_len]
    i = 0
    while len(new_date_index) != pred_len:
        i += 1
        new_date_index = pd.date_range(start_time, start_time + datetime.timedelta(days=pred_len // 5 * 7 + i),
                                       freq='B')

    pred_final = np.load(f"{result_folder_path}/real_prediction/j+{pred_lens[-1]}.npy")[-1, :, -1]
    test_final = np.load(f"{result_folder_path}/pred/j+{pred_lens[-1]}.npy")[-1, :, -1]
    true_final = np.load(f"{result_folder_path}/true/j+{pred_lens[-1]}.npy")[-1, :, -1]
    data_MSE = [MSE(test_final, true_final)]
    data_MAE = [MAE(test_final, true_final)]
    data_RSE = [RSE(test_final, true_final)]

    for pred_len in pred_lens[-2::-1]:
        real_prediction = np.load(f"{result_folder_path}/real_prediction/j+{pred_len}.npy")[-1, :, -1]
        test = np.load(f"{result_folder_path}/pred/j+{pred_len}.npy")[-1, :, -1]
        true = np.load(f"{result_folder_path}/true/j+{pred_len}.npy")[-1, :, -1]

        pred_final = np.concatenate((real_prediction, pred_final[pred_len:]))
        test_final = np.concatenate((test, test_final[pred_len:]))
        true_final = np.concatenate((true, true_final[pred_len:]))

        test = np.load(f"{result_folder_path}/pred/j+{pred_len}.npy")
        true = np.load(f"{result_folder_path}/true/j+{pred_len}.npy")

        data_MSE.append(MSE(test, true))
        data_MAE.append(MAE(test, true))
        data_RSE.append(RSE(test, true))

    data_MSE.append(MSE(test_final, true_final))
    data_MAE.append(MAE(test_final, true_final))
    data_RSE.append(RSE(test_final, true_final))

    date_pred = pd.Series(pred_final, index=new_date_index.date)
    date_pred.name = "Close_pred"
    data_for_app = pd.concat([dataset, date_pred], axis=1)

    if not os.path.exists(data_app):
        os.makedirs(data_app)

    data_for_app.index.name = 'date'
    data_for_app = data_for_app.rename(columns={'OT': 'Close', 'Close_pred': 'Prediction'})
    data_for_app.to_csv(f"{data_app}/close.csv")

    fig = px.line(data_for_app)
    fig.write_html(f"{pipeline_path}my_visualisation.html", full_html=False, div_id='plotly-figure', include_plotlyjs='directory')

    src = f"{pipeline_path}my_visualisation.html"
    dst = f"{target_path}templates/plotly_graphe/{key}.html"
    shutil.copyfile(src, dst)

    data = []
    data.append(data_for_app['Close'].dropna().index.max())
    data.append(data_for_app['Close'].loc[data_for_app['Close'].dropna().index.max()])

    for pred_len in [1, 15, 30, 61, 91, 182, 365]:
        data.append(data_for_app['Prediction'].dropna().values[int(pred_len / 7 * 5)])

    for i in range(2, len(data)):
        data[i] = f"{(1 - data[1] / data[i]):.2%}"
        data_MSE[i - 2] = f"{(int(data_MSE[i - 2])):}"
        data_MAE[i - 2] = f"{(data_MAE[i - 2]):.2f}"
        data_RSE[i - 2] = f"{(data_RSE[i - 2]):.2f}"

    data_MSE[-1] = f"{int(data_MSE[-1]):.2f}"
    data_MAE[-1] = f"{(data_MAE[-1]):.2f}"
    data_RSE[-1] = f"{(data_RSE[-1]):.2f}"

    data_MSE.append("MSE")
    data_MAE.append("MAE")
    data_RSE.append("RSE")

    data_MSE = data_MSE[::-1]
    data_MAE = data_MAE[::-1]
    data_RSE = data_RSE[::-1]

    data[1] = f"{data[1]:.2f}"

    index_tab = pd.DataFrame(data=[data, data_MSE, data_MAE, data_RSE],
                             columns=["last update", "last close", "+1j", "+15j", "+30j", "+61j", "+91j", "182j",
                                      "365j"])

    index_tab.to_html(f"{pipeline_path}tab.html", index=False, justify="center")
    src = f"{pipeline_path}tab.html"
    dst = f"{target_path}templates/table/tab_{key}.html"
    shutil.copyfile(src, dst)


if __name__ == "__main__":
    print("load data")
    load_fresh_data(keys_selected_index=keys_selected_index)
    for key in keys_selected_index:
        for projection in projections:
            print(key, projection)
            start_training(key=key, pred_len=projection, seq_len=max(30, projection))
        import_training_result(key, pred_lens=projections)
