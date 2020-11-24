from apps.db.mongo_connection import PyMongo


class RFMData:
    def __init__(self):
        self.db = PyMongo().get_db_connection()
        self.end_dates = []
        self.rfm = []

    def get_all_end_dates(self):
        print('Calling end dates')
        print(self.db.Rfmsample.distinct('end_date'))
        # Get end dates and return a list of all end dates
        return self.db.Rfmsample.distinct('end_date')

    def get_records(self):
        print('Calling get records')
        cursor = self.db.Rfmsample.find({},
                                  {'R': 1, 'F': 1, 'M': 1, '_id': 0, 'organization_id': 1, 'start_date': 1,
                                   'end_date': 1, 'RFM': 1})
        for item in cursor:
            my_items = {}

            # Retrieve r,f,m objects
            r_values = item.pop('R', {})
            f_values = item.pop('F', {})
            m_values = item.pop('M', {})
            rfm_values = item.pop('RFM', {})
            segments = rfm_values.pop('segments', {})
            segment_a = segments.pop('A', {})
            segment_b = segments.pop('B', {})
            segment_c = segments.pop('C', {})
            segment_d = segments.pop('D', {})
            segment_e = segments.pop('E', {})

            my_items.update(item)
            my_items.update(rfm_values)
            my_items.update(segments)

            # Get individual customer id's of a particular score - R
            my_items["R_score1"] = r_values['score'][1].pop('customer_ids', {})
            my_items["R_score2"] = r_values['score'][2].pop('customer_ids', {})
            my_items["R_score3"] = r_values['score'][3].pop('customer_ids', {})
            my_items["R_score4"] = r_values['score'][4].pop('customer_ids', {})
            my_items["R_score5"] = r_values['score'][5].pop('customer_ids', {})

            # Get individual customer id's of a particular score - F
            my_items["F_score1"] = f_values['score'][1].pop('customer_ids', {})
            my_items["F_score2"] = f_values['score'][2].pop('customer_ids', {})
            my_items["F_score3"] = f_values['score'][3].pop('customer_ids', {})
            my_items["F_score4"] = f_values['score'][4].pop('customer_ids', {})
            my_items["F_score5"] = f_values['score'][5].pop('customer_ids', {})

            # Get individual customer id's of a particular score - M
            my_items["M_score1"] = m_values['score'][1].pop('customer_ids', {})
            my_items["M_score2"] = m_values['score'][2].pop('customer_ids', {})
            my_items["M_score3"] = m_values['score'][3].pop('customer_ids', {})
            my_items["M_score4"] = m_values['score'][4].pop('customer_ids', {})
            my_items["M_score5"] = m_values['score'][5].pop('customer_ids', {})

            # Get RFM segment-wise customer ids
            my_items["segment_a"] = segment_a['customer_ids']
            my_items["segment_b"] = segment_b['customer_ids']
            my_items["segment_c"] = segment_c['customer_ids']
            my_items["segment_d"] = segment_d['customer_ids']
            my_items["segment_e"] = segment_e['customer_ids']

            self.rfm.append(my_items)
        return self.rfm






