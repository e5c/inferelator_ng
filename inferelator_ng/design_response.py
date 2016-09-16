"""
Create design and response matrices.
"""

import pandas as pd
import math


def is_nan(x):
    if type(x) is float:
        return math.isnan(x)
    else:
        return False


def metadata_tsv_column_map(column_name):
    column_map = {"isTs" : "is_ts",
                  "is1stLast" : "is_first_last",
                  "prevCol" : "prev_col",
                  "del.t" : "del_t",
                  "condName" : "condition_name"}
    return column_map[column_name]


def load_metadata_df(metadata_file):
    metadata_df = pd.read_csv(metadata_file, sep=',', index_col=0, dtype={"del.t": float})
    metadata_df.columns = [metadata_tsv_column_map(x) for x in metadata_df.columns]
    return metadata_df


def load_expression_df(expression_file):
    expression_df = pd.read_csv(expression_file, sep=',', index_col=0)
    return expression_df


def calculate_design_and_response(self,
                                  metadata_df,
                                  expression_df,
                                  del_t_min,
                                  del_t_max,
                                  tau):
    """
    Returns design and response matrices.
    # design matrix is same as exp.mat leaving out last time points
    # response matrix is same as design for steady state; linear interpolation else

    Parameters
    -----------
    metadata_df : pd.DataFrame with columns
    expression_df :
    del_t_min :
    del_t_max :
    tau :
    """

    # check if there are condition names missing in expression matrix
    missing_condition_names = set(expression_df.columns).difference(set(metadata_df["condName"]))
    if missing_condition_names != set():
        print(", ".join(missing_condition_names))
        raise ValueError("Error when creating design and response. The conditions printed above are in the "
                         "metadata, but not in the expression matrix")

    # break time series if del_t is larger than del_t_max
    metadata_df.ix[metadata_df.del_t > del_t_max, 'prev_col'] = float('nan')
    metadata_df.ix[metadata_df.del_t > del_t_max, 'del_t'] = float('nan')

    # handle steady state conditions:
    # "steady state" := rows in which prev_col is nan, and condition_name != prev_col
    # get the `cond` columns in expression_df that correspond to
    # the `cond` in metadata_df that are 'steady'
    steady_metadata_df = metadata_df.ix[
        (metadata_df['prev_col'].apply(lambda x: is_nan(x))) &
        (metadata_df.prev_col != metadata_df.condition_name)]
    steady_conditions_series = steady_metadata_df['condition_name']

    steady_design_df = expression_df[list(steady_conditions_series)]
    steady_response_df = steady_design_df.copy(deep=True)

    # handle time series
    # TO DO: fill in

    # dummy return values for now
    design = pd.DataFrame()
    response = pd.DataFrame()
    return design, response


class DesignResponseCalculator:
    """
    Class to hold typical arguments when wanting to calculate design and response matrices.
    """
    def __init__(self,
                 metadata_file,
                 expression_file,
                 response_file="response.tsv",
                 design_file="design.tsv",
                 del_t_min=0,
                 del_t_max=110,
                 tau=45):
        # TO DO: do path checks / creation
        self.metadata_df = load_metadata_df(metadata_file)
        self.expression_df = load_expression_df(expression_file)
        self.response_file = response_file
        self.design_file = design_file
        self.del_t_min = del_t_min
        self.del_t_max = del_t_max
        self.tau = tau

    def run(self):
        expression_df = pd.read_csv(self.expression_file,
                                    sep='\t')

        metadata_df = pd.read_csv(self.metadata_file,
                                  sep='\t')
        metadata_df.columns = metadata_df.columns.apply(metadata_tsv_column_map)

        # design.and.response(meta.data, exp.mat, delT.min, delT.max, tau)
        design, response = calculate_design_and_response(metadata_df,
                                                         expression_df,
                                                         self.delTmin,
                                                         self.delTmax,
                                                         self.tau)

        # TO DO: proper `os.path` wrappers to write these to the correct place.
        design.to_csv(self.design_file)
        response.to_csv(self.response_file)

