import os

import numpy as np
import pandas as pd


README_headers = {
    "Cone": "## Experimental Conditions: Cone Calorimeter ",
    "MCC": "## Experimental Conditions: Microscale Combustion Calorimetry (MCC)",
    "TGA": "## Experimental Conditions: Thermogravimetric Analysis (TGA)"}


def NETZSCH_read_raw_column_labels(file_path, csv_delimiter=";", thousands=".", decimal=",",
                                   encoding='latin-1', header=0, nrows=1):
    """
    Read a single line of the csv file to extract the column labels as a list.
    """

    raw_column_labels = list(
        pd.read_csv(
            file_path,
            delimiter=csv_delimiter,
            thousands=thousands,
            decimal=decimal,
            encoding=encoding,
            header=header,
            nrows=nrows))

    return raw_column_labels



def NETZSCH_read_cone_settings(file_path, csv_delimiter=";", thousands=".", decimal=",",
                               encoding='latin-1', usecols=[0, 1], header=None,
                               skip_blank_lines=True, on_bad_lines="skip",
                               names=["key", "value"], how_dropna="all"):
    """
    Reads the first two columns of a NETZSCH cone file and creates a dictionary.
    """

    cone_settings = (pd.read_csv(
        file_path,
        delimiter=csv_delimiter,
        thousands=thousands,
        decimal=decimal,
        encoding=encoding,
        header=header,
        names=names,
        usecols=usecols,
        skip_blank_lines=skip_blank_lines,
        on_bad_lines=on_bad_lines
    )
    .dropna(how=how_dropna)     # "all": drop rows like ","
    .set_index("key")["value"]  # make first column the dict key
    .replace({np.nan: None}    # turn NaN into None
                    )
    .to_dict())

    return cone_settings



def NETZSCH_read_raw_cone_data(file_path, usecols, csv_delimiter=";", thousands=".", decimal=",",
                               encoding='latin-1', header=0, skiprows=[1], index_col=False):
    """
    Reads the NETZSCH cone data, without the cone settings in the first two columns.
    """

    cone_data = pd.read_csv(
        file_path,
        delimiter=csv_delimiter,
        thousands=thousands,
        decimal=decimal,
        encoding=encoding,
        header=header,
        skiprows=skiprows,
        index_col=index_col,
        usecols=usecols)#.dropna(how='all')

    return cone_data


def NETZSCH_cone_adjust_time(cone_meta_data, cone_data_raw, start_time="Test start time (s)",
                             time_header="time (s)"):

    # Get the start time of the experiment
    start_time = float(cone_meta_data[start_time])

    # Create deep copy of the DataFrame
    cone_data = cone_data_raw.copy()

    # Adjust the time column
    cone_data[time_header] -= start_time

    return cone_data


def read_cone_data(cone_file_path, manufacturer="NETZSCH"):
    if manufacturer == "NETZSCH":
        # Get raw column labels
        raw_column_labels = NETZSCH_read_raw_column_labels(file_path=cone_file_path)

        # Read the cone settings
        cone_settings = NETZSCH_read_cone_settings(file_path=cone_file_path)

        # Read the raw cone data, skip first two columns with meta data
        cone_data_raw = NETZSCH_read_raw_cone_data(file_path=cone_file_path,
                                                   usecols=raw_column_labels[2:])

        # Adjust the time to set the actual start at 0s
        cone_data_adj = NETZSCH_cone_adjust_time(cone_meta_data=cone_settings,
                                                 cone_data_raw=cone_data_raw)

        return cone_settings, cone_data_adj



def NETZSCH_read_TGA_file(file_path, encoding="cp1252", header_indicator="##", column_sep=";"):
    """
    Read files produced from a NETZSCH TGA device.
    """

    meta = dict()
    header_idx = None  # line index of the header row (0-based)

    # 1.1) Collect meta data and determine where the table starts
    with open(file_path, encoding=encoding) as file_content:
        for idx, raw_line in enumerate(file_content):
            line = raw_line.strip()

            # Separator line
            if header_indicator in line:
                header_idx = idx-1   # header is this line
                break

            # Collect "key: value" pairs from metadata
            if column_sep in line:
                key, value = line.split(column_sep, maxsplit=1)
                value = value.strip()

                try:
                    # Try to convert values to float
                    value = float(value)
                except ValueError:
                    # Keep original value
                    value = value
                # Store data
                key = key.strip()
                key = key[1:-1]
                meta[key.strip()] = value

    # 2.1) Read the table
    data_df = pd.read_csv(
        file_path,
        sep=column_sep,
        encoding=encoding,
        engine="python",
        header=header_idx,
        comment=None,           # in case later lines have '#', don't treat as comments
        skip_blank_lines=True
    )

    # 2.2) Adjust the first column header
    headers = list(data_df)
    if '##Temp./ï¿½C' in headers:
        data_df.rename({'##Temp./ï¿½C': 'Temp./°C'}, axis='columns', inplace=True)
    else:
        data_df.rename({'##Temp./°C': 'Temp./°C'}, axis='columns', inplace=True)

    return meta, data_df



def DEATAK_read_MCC_file(file_path, encoding="utf-8", line_sep="@", column_sep="\t"):
    """
    Read files produced from a DEATAK MCC device.
    """

    meta = dict()
    header_idx = None  # line index of the header row (0-based)

    # 1.1) Collect meta data and determine where the table starts
    with open(file_path, encoding=encoding) as file_content:
        for idx, raw_line in enumerate(file_content):
            line = raw_line.strip()

            # Separator line
            if line == line_sep:
                header_idx = idx + 1   # header is the next line
                print('header_idx', header_idx)
                break

            # Collect "key: value" pairs from metadata
            if ":" in line:
                key, value = line.split(":", maxsplit=1)
                value = value.strip()

                try:
                    # Try to convert values to float
                    value = float(value)
                except ValueError:
                    # Keep original value
                    value = value
                # Store data
                meta[key.strip()] = value

    # 1.2) Clean up the T Correction Coefficients
    T_corr_coeff_key = 'T Correction Coefficients'
    if T_corr_coeff_key in meta:
        T_coeff = meta[T_corr_coeff_key]
        T_coeff = [float(token) for token in T_coeff.split(column_sep)]
        meta[T_corr_coeff_key] = T_coeff

    # 2) Read the table
    data_df = pd.read_csv(
        file_path,
        sep=column_sep,
        encoding=encoding,
        engine="python",
        header=header_idx,
        comment=None,           # in case later lines have '#', don't treat as comments
        skip_blank_lines=True
    )

    return meta, data_df


def dict_to_md(table_dict_top, table_dict_bottom=None):
    """
    Converts a dictionary into a Markdown table.

    Expects each key-value pair to be a column.
    Column content should be a list.

    Returns a list of strings, each list element is a line.
    """

    table_list = list()

    headers = list(table_dict_top)
    n_cols = len(headers)

    n_lines = len(table_dict_top[headers[0]])
    n_lines_bottom = len(table_dict_bottom[headers[0]])

    # Table layout control elements
    line_start = "|"
    hline_left = ' :---- |'  # column left justified
    hline_right = ' ----: |'  # column right justified
    hline_centered = ' :----: |'  # column centered

    # Build header line
    line = line_start
    line += f" {' | '.join(map(str, headers))} |"
    table_list.append(line)

    # Draw horizontal line
    line = line_start
    line += n_cols * hline_left
    table_list.append(line)

    # Populate table body (top)
    for idx in range(n_lines):
        line = line_start
        for header in headers:
            cell = str(table_dict_top[header][idx])
            line += f" {cell.replace('.csv', '')} |"
        table_list.append(line)

    # Populate table body (bottom)
    if table_dict_bottom is not None:
        for idx in range(n_lines_bottom):
            line = line_start
            for header in headers:
                cell = str(table_dict_bottom[header][idx])
                line += f" {cell.replace('.csv', '')} |"
            table_list.append(line)

    return table_list


def linear_baseline(df, t_label, T_label, hrr_label, time_intervals):
    """
    Linear base line adjustment for MCC data.
    Uses two intervals at the beginning and end
    of the experiment to conduct a linear fit.

    Returns polynomial coefficients (m, b).
    """

    # Create mask of first time interval
    t_1, t_2 = time_intervals[0]
    t = df[t_label]
    mask_1 = ((t_1 < t) & (t < t_2))

    # Create mask of second time interval
    t_3, t_4 = time_intervals[1]
    mask_2 = ((t_3 < t) & (t < t_4))

    # Join masks (keep True)
    mask = np.logical_or(mask_1, mask_2)


    # Get temperatures from the intervals
    T_fit = df[T_label].loc[mask]
    # Get HRR from intervals
    HRR_fit = df[hrr_label].loc[mask]

    # Compute linear fit as baseline
    m, b = np.polyfit(T_fit, HRR_fit, 1)

    return (m, b)  # p, i.e. the polynomial coefficients


def to_bullet_points(exp_summary, indent=0, bullet="-"):
    """
    Takes a nested dictionary and converts it into markdown bullet points.
    """

    # Initialise level
    level=0

    # Prepare result collection
    lines = list()

    if isinstance(exp_summary, dict):
        # Deal with nested bullet points
        items = exp_summary.items()

        for key, value in items:
            # Create padding with spaces
            pad = indent * " "

            if isinstance(value, dict):
                # Deal with nested bullet points
                lines.append(f"{pad}{bullet} {key}")
                lines.extend(to_bullet_points(value, indent=indent+4, bullet=bullet))

            elif isinstance(value, list):
                # Transform lists to string
                lines.append(f"{pad}{bullet} {key}: {', '.join(map(str, value))}")

            else:
                # The base case
                lines.append(f"{pad}{bullet} {key}: {value}")
    else:
        pass

    return lines


def write_README(README_content, README_path, encoding="utf-8", newline='\n'):
    """
    Wrties a list of strings to a text file, line by line.
    """

    with open(README_path, 'w', encoding=encoding, newline=newline) as file_handler:
        for line in README_content:
            file_handler.write(f"{line}"+newline)




def get_window_points(phi, Δ_phi):
    
    # Get resolution
    d_phi = np.median(np.diff(phi))
    
    # Determine window size for smoothing
    win_pts = int(round(Δ_phi / d_phi))
    win_pts = max(win_pts, 5)
    
    # Ensure odd number window size
    if win_pts % 2 == 0:
        win_pts += 1
        
    return win_pts


def H_baseline(m_0, dT_dt, c_T, m_t):
    """
    Compute sensible heat flow baseline, to later determine the specific heat capacities.

    From: Formula 11 in 'Measurement of kinetics and thermodynamics of the
    thermal degradation for non-charring polymers',
    Jing Li, Stanislav I.Stoliarov, Combustion and Flame 160 (2013) 1287–1297
    https://doi.org/10.1016/j.combustflame.2013.02.012
    https://doi.org/10.1016/j.polymdegradstab.2013.09.022

    :param m_0: initial sample mass [mg]
    :param dT_dt: instantaneous heating rate [K/s]
    :param c_T: list of c_j [J / (kg K)]
    :param m_t: list of m_j [mg]
    :return: baseline as numpy.ndarray
    """

    c_m = list()

    for i, c_i_T in enumerate(c_T):
        c_m_i = c_i_T * m_t[i]
        c_m.append(c_m_i)

    if len(c_m) > 1:
        sum_c_m = np.sum(c_m, axis=0)
    else:
        sum_c_m = c_m[0]

    baseline = 1/m_0 * dT_dt * sum_c_m

    return baseline
