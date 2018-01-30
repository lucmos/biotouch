#import bob
class IdentificationEvaluator:
    def __init__(self, cms_probabilities , y_test, class_list):
        self.cms_values=[]
        assert len(y_test)==len(cms_probabilities)

        #def fill_cms_values():
        i=0
        while(i<len(class_list)):
            cms_val_i = 0
            for prob_list, y in zip(cms_probabilities, y_test):
                y_prob=prob_list[y_test.index(y)]
                numberOfGreater = 0
                for a in prob_list:
                    if (((prob_list.index(a)<y_test.index(y)) and (a>=y_prob))or((prob_list.index(a)>y_test.index(y)) and (a>y_prob))):
                            numberOfGreater+=1
                if numberOfGreater<=i:
                    cms_val_i+=1
                    print(cms_val_i)
            self.cms_values.append(cms_val_i/len(y_test))
            i+=1
        print(self.cms_values)

        #bob.measure.plot.cmc(self.cms_values, logx=True, **kwargs)

if __name__ == '__main__':
    l = IdentificationEvaluator([[ 0.96697155  ,0.03302845],[ 0.00746219  ,0.99253781],[ 0.00951699  ,0.99048301],[ 0.95638103  ,0.04361897],
                                 [ 0.8036171   ,0.1963829 ],[ 0.8036171   ,0.1963829 ],[ 0.8036171   ,0.1963829 ],[ 0.01786314  ,0.98213686],
                                 [ 0.96559608  ,0.03440392],[ 0.96077084  ,0.03922916],[ 0.01264261  ,0.98735739],[ 0.81518927  ,0.18481073],
                                 [ 0.01102044  ,0.98897956],[ 0.95441381  ,0.04558619],[ 0.94432064  ,0.05567936],[ 0.00675033  ,0.99324967],
                                 [ 0.00960538  ,0.99039462],[ 0.96840267  ,0.03159733],[ 0.95344436  ,0.04655564],[ 0.02739944  ,0.97260056]],

                                ["adriano_ischiboni_was-lx1a_0_ITALIC","alessandro_spini_was-lx1a_0_ITALIC","alessandro_spini_was-lx1a_0_ITALIC",
                                "adriano_ischiboni_was-lx1a_0_ITALIC","alessandro_spini_was-lx1a_0_ITALIC","adriano_ischiboni_was-lx1a_0_ITALIC",
                                "alessandro_spini_was-lx1a_0_ITALIC","alessandro_spini_was-lx1a_0_ITALIC",
"adriano_ischiboni_was-lx1a_0_ITALIC",
"adriano_ischiboni_was-lx1a_0_ITALIC",
"alessandro_spini_was-lx1a_0_ITALIC",
"adriano_ischiboni_was-lx1a_0_ITALIC",
"alessandro_spini_was-lx1a_0_ITALIC",
"adriano_ischiboni_was-lx1a_0_ITALIC",
"adriano_ischiboni_was-lx1a_0_ITALIC",
"alessandro_spini_was-lx1a_0_ITALIC",
"alessandro_spini_was-lx1a_0_ITALIC",
"adriano_ischiboni_was-lx1a_0_ITALIC",
"adriano_ischiboni_was-lx1a_0_ITALIC",
"alessandro_spini_was-lx1a_0_ITALIC"]          ,[
    "adriano_ischiboni_was-lx1a_0_ITALIC",
    "alessandro_spini_was-lx1a_0_ITALIC"
]  )
   # l.fill_cms_values()
