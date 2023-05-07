import flask
from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import random
import numpy as np, scipy.stats as st

app = Flask(__name__)
CORS(app)


def analyse(dataset):
    analysis = {}
    analysis['totalColumns'] = len(dataset)
    # for column in dataset:
    #     df = np.array(dataset[column])
    #     print(df.dtype)
    #     print(df)
    #     if df.dtype == 'int64' or df.dtype == 'float64' or df.dtype == 'int32' or df.dtype == 'float32':
    #         analysis['bp_data'][column] = {
    #             'min': np.min(df),
    #             'max': np.max(df),
    #             'mean': np.mean(df),
    #             'median': np.median(df),
    #             'sd': np.std(df),
    #             'missing': len(dataset[column]) - len(df),
    #             'q1': np.quantile(df, 0.25),
    #             'q3': np.quantile(df, 0.75),
    #             '95Ci': st.t.interval(0.95, len(df)-1, loc=np.mean(df), scale=st.sem(df)),
    #             '99Ci': st.t.interval(0.99, len(df)-1, loc=np.mean(df), scale=st.sem(df))
    #         }


    

    for column in dataset:
        if type(dataset[column]) == list:
            ls_data = [x for x in dataset[column]
                       if type(x) == int or type(x) == float]
            length = len(ls_data)
            sm = sum(ls_data)
            std = (sum([(x - sm/length)**2 for x in ls_data])/(length-1))**0.5
            if length > 0:
                analysis[column] = {
                    'min': min(ls_data),
                    'max': max(ls_data),
                    'mean': sm/length,
                    'median': sorted(ls_data)[length//2],
                    'sd': std,
                    'missing': len(dataset[column]) - length,
                    'quartile1': sorted(ls_data)[length//4],
                    'quartile3': sorted(ls_data)[3*length//4],
                    '95ConfidenceInterval': [sm/length - 1.96*std/(length**0.5), sm/length + 1.96*std/(length**0.5)],
                    '99ConfidenceInterval': [sm/length - 2.58*std/(length**0.5), sm/length + 2.58*std/(length**0.5)],
                    'correlations': [
                        {
                            'column': col,
                            'correlation': np.corrcoef(ls_data, dataset[col])[0][1]
                        } for col in dataset if type(dataset[col]) == list and col != column and len(dataset[col]) == length
                    ],
                    'ttests': {
                        'explanation': 'If Significant difference is true it means that the two groups are probably different from each other.',
                        'results': [
                        {
                            'column': col,
                            'ttest': {
                                'p': st.ttest_ind(ls_data, dataset[col])[1],
                                'significantDifference': bool(st.ttest_ind(ls_data, dataset[col])[1] < 0.95)
                            }
                        } for col in dataset if type(dataset[col]) == list and col != column and len(dataset[col]) == length
                    ]
                    }
                }
    return analysis
    


@app.route('/', methods=['POST'])
def api():
    dataset = request.get_json()
    if not dataset:
        return "No data received", 400
    return jsonify(analyse(dataset))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
