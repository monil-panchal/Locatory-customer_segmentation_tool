from apps.db.mongo_connection import PyMongo


class RFMData:
    def __init__(self):
        self.db = PyMongo().get_db_connection()
        self.end_dates = []
        self.rfm = []

    def get_all_end_dates(self, object_value):
        # Get end dates and return a list of all end dates
        cursor = self.db.RFMSegments.find(
            {'segmentation_parameters_id': object_value}, {'end_date': 1})
        end_dates = []
        for item in cursor:
            end_dates.append(item['end_date'])
        return end_dates

    def get_records(self, object_value):
        cursor = self.db.RFMSegments.find(
            {'segmentation_parameters_id': object_value})
        for item in cursor:
            my_items = {}

            # Retrieve r,f,m objects
            r_values = item.pop('R', {})
            f_values = item.pop('F', {})
            m_values = item.pop('M', {})
            rfm_values = item.pop('RFM', {})

            # Get individual scores
            r_scores = r_values.pop('score', {})
            f_scores = f_values.pop('score', {})
            m_scores = m_values.pop('score', {})
            segments = rfm_values.pop('segments', {})

            # Get r-score key list
            keys_list = list(r_scores.keys())

            # Store length of segments:
            len_val = item['segment_count']

            # R values
            for values in list(r_scores.keys()):
                r_var = "R_score" + values
                globals()[r_var] = r_scores.pop(values, {})

            # F, M values
            for i in range(len_val):
                f_var = "F_score" + str(i + 1)
                globals()[f_var] = f_scores.pop(str(i + 1), {})
                m_var = "M_score" + str(i + 1)
                globals()[m_var] = m_scores.pop(str(i + 1), {})

            # RFM values
            # Check if segments exist
            for i in range(len_val):
                # Map number to segment letter
                val = "segment_" + chr(65 + i)
                globals()[val] = segments.pop(chr(65 + i), {})

            my_items.update(item)
            my_items.update(rfm_values)
            my_items.update(r_values)
            my_items.update(f_values)
            my_items.update(m_values)
            my_items.update(segments)
            my_items.update(r_scores)
            my_items.update(f_scores)
            my_items.update(m_scores)

            # Append keys to r_keys
            my_items["r_keys"] = keys_list

            # Get R score-wise customer ids
            for values in keys_list:
                r_var_name = "R_score" + values
                my_items[r_var_name] = globals()[r_var_name]['customer_ids']

            # Get F, M score-wise customer ids
            for i in range(len_val):
                f_var_name = "F_score" + str(i + 1)
                my_items[f_var_name] = globals()[f_var_name]['customer_ids']

                m_score_name = "M_score" + str(i + 1)
                my_items[m_score_name] = globals(
                )[m_score_name]['customer_ids']

            # Get RFM segment-wise customer ids
            for i in range(len_val):
                val = "segment_" + chr(65 + i)
                my_items[val] = globals()[val]['customer_ids']

            self.rfm.append(my_items)
        return self.rfm

    def get_segment_size(self, object_value):
        cursor = self.db.RFMSegments.find(
            {'segmentation_parameters_id': object_value}, {'segment_count': 1})
        for item in cursor:
            # Return the segment size
            return item["segment_count"]
