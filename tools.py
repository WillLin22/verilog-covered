class Assign_Graph():
    """
    生成assign图，同时内部各功能独立，可以作为单独的工具类来进行复用
    """
    def get_vars(self, expressions, get_width=False):
        """
        A list that contains all the variable names in the code, each for exactly once
        
        Returns:
            list: a list of variable names or (var_name, var_width) if get_width is set to true
            
        """
        vars = set()
        vars_with_width = list()
        for i, e in enumerate(expressions[1:]):
            if e.name != None and e.name not in vars:
                vars.add(e.name)
                vars_with_width.append((e.name, e.value.width))
        return list(vars)
    
    def ast_traversal(self, e, expressions, get_ls=lambda e, tr: tr[e.left] if e.left != 0 else None, get_rs=lambda e, tr:tr[e.right] if e.right != 0 else None, info_func=lambda x: x):
        """
        A tool function that return a list of all info appeared in a given ast tree. The info is determined by the info_func function.
        
        Returns:
            list: a list of all selected info appeared in the ast tree, each for exactly once
        """
        if e == None:
            return []
        left = get_ls(e, expressions)
        right = get_rs(e, expressions)
        vars = set([info_func(e)] if info_func(e) else [] + self.ast_traversal(left, expressions, info_func=info_func) + self.ast_traversal(right, expressions, info_func=info_func))
        return list(vars) if vars != None else []
    def get_adj_list(self, vars, expressions):
        adj_list = {var: [] for var in vars}
        for i, e in enumerate(expressions[1:]):
            if e.father == None:
                left = expressions[e.left]
                right = expressions[e.right]
                if left.name != None:
                    adj_list[left.name] += self.ast_traversal(right, expressions, info_func=lambda x: x.name if x.name != None else None)
                    adj_list[left.name] = list(set(adj_list[left.name]))
        return adj_list
    def get_back_adj_list(self, vars, expressions):
        back_adj_list = {var: [] for var in vars}
        for i, e in enumerate(expressions[1:]):
            if e.father == None:
                left = expressions[e.left]
                right = expressions[e.right]
                vars = self.ast_traversal(right, expressions, info_func=lambda x: x.name if x.name != None else None)
                for var in vars:
                    if left.name != None:
                        back_adj_list[var].append(left.name)
        return back_adj_list
    def get_dists_between_vars(self, vars, adj_list):
        """
        Get the distance between each pair of variables in the adj_list.
        The distance is defined as the number of edges in the shortest path between the two variables.
        
        Returns:
            dict:dict[v1name: dict[v2name, dist]], a dict that contains the distance between each pair of variables
        """
        dists = {var: {v: float('inf') if v != var else 0 for v in vars} for var in vars}
        updated = []
        def update_dists(v, adj_list):
            next_vars = adj_list[v]
            for nv in next_vars:
                if nv not in updated:
                    update_dists(nv, adj_list)
            for nv in next_vars:
                dists[v][nv] = 1
                for k, dist in dists[nv].items():
                    if dist != float('inf'):
                        dists[v][k] = min(dists[v][k], dist + 1)
            updated.append(v)
        for var in vars:
            update_dists(var, adj_list)
        for var in vars:
            for nvar, dist in dists[var].items():
                if dist == float('inf') and dists[nvar][var] != float('inf'):
                    dists[var][nvar] = -dists[nvar][var]
        return dists
    def run(self, expressions):
        """
        aka get_vars -> get_adj_list -> get_dists_between_vars
        """
        vars = self.get_vars(expressions)
        adj_list = self.get_adj_list(vars, expressions)
        dists = self.get_dists_between_vars(vars, adj_list)
        return dists

class Fault_Locate_Analyzer_Factory():
    """
    A factory class that creates a Fault_Locate_Analyzer object based on the given type.
    """
    def create(self, dists, vars_limit=10, dist_factor=lambda x, d: x * 0.9 ** d if d != float('inf') else 0, type=3):
        """
        Args:
            dists (dict[str, Dict[str, int]]): the distance between each pair of variables. If assign v1 = v2, then
                dists[v1][v2] = 1, dists[v2][v1] = -1, and dists[v1][v1] = 0.
            faulty_var (str): the name of the faulty variable.
            located_var_lists (list[tuple(str, int)]): a list of varname and its weight in the analysis.
            vars_limit (int): the number of variables to be considered in the analysis, default is 10.
            dist_factor (function(score, dist) : float): a function that takes the score and distance as input and returns a float.
            type (int): the type of the Fault_Locate_Analyzer to be created, default is 3.
        """
        analyzer = object()
        if type == 1:
            analyzer = Fault_Locate_Analyzer_Simple(dists, vars_limit, dist_factor)
        elif type == 2:
            analyzer = Fault_Locate_Analyzer_2(dists, vars_limit, dist_factor)
        elif type == 3:
            analyzer = Fault_Locate_Analyzer_3(dists, vars_limit, dist_factor)
        else:
            raise ValueError(f"Invalid type: {type}. Must be 1, 2 or 3.")
        return analyzer

class Fault_Locate_Analyzer():
    def __init__(self, dists, vars_limit=10, dist_factor=lambda x, d: x * 0.9 ** d if d != float('inf') else 0):
        """
        Args:
            dists (dict[str, Dict[str, int]]): the distance between each pair of variables. If assign v1 = v2, then
                dists[v1][v2] = 1, dists[v2][v1] = -1, and dists[v1][v1] = 0.
            faulty_var (str): the name of the faulty variable.
            located_var_lists (list[tuple(str, int)]): a list of varname and its weight in the analysis.
            vars_limit (int): the number of variables to be considered in the analysis, default is 10.
            dist_factor (function(score, dist) : float): a function that takes the score and distance as input and returns a float.
        """
        self.vars = [var for var, _ in dists.items()]
        self.dists = dists
        self.vars_limit = vars_limit
        self.dist_factor = dist_factor
    def error_handler(self):
        error = self.faulty_var not in self.vars
        if error:
            print(f'Error: You did not give a faulty var name or the name is invalid! Faulty var name: {self.faulty_var}')
            return False
        return True
    def analyse(self, faulty_var, located_var_lists):
        """
        Analyse how good the current fault location is and return a score based on the top n located variables and its weight.
        
        Returns:
            float: the score of the fault location, the higher the better.
        """
        raise NotImplementedError("This method should be implemented in the subclass.")
    
    
class Fault_Locate_Analyzer_Simple(Fault_Locate_Analyzer):
    def analyse(self, faulty_var, located_var_lists):
        self.faulty_var = faulty_var
        if not self.error_handler():
            return 0.0
        self.sorted_var_lists = sorted(located_var_lists, key=lambda x: x[1], reverse=True)
        score = {var: 0 for var in self.vars}
        for i, (var, weight) in enumerate(self.sorted_var_lists[:self.vars_limit]):
            score[var] += weight
            for v, dist in self.dists[var].items():
                if dist != float('inf') and dist > 0:
                    score[v] += self.dist_factor(weight, dist)
                    
        return score[self.faulty_var] / sum([s for _, s in score.items()])
class Fault_Locate_Analyzer_2(Fault_Locate_Analyzer):
    """base score: weight / max weight
    get the best score from the top self.vars_limit variables considering its distance with self.dist_factor(score, dist)
    """
    def analyse(self, faulty_var, located_var_lists):
        self.faulty_var = faulty_var
        if not self.error_handler():
            return 0.0
        self.sorted_var_lists = sorted(located_var_lists, key=lambda x: x[1], reverse=True)
        return max(self.dist_factor(w/max(w for (s, w) in self.sorted_var_lists[:self.vars_limit]), abs(self.dists[s][self.faulty_var])) for (s, w) in self.sorted_var_lists[:self.vars_limit] if s in self.dists and self.faulty_var in self.dists[s] and self.dists[s][self.faulty_var] != float('inf'))
    
    
class Fault_Locate_Analyzer_3(Fault_Locate_Analyzer):
    """
    Get the closest result from the top self.vars_limit variables and return its score.
    The base score is weight/max(weight)
    """
    def analyse(self, faulty_var, located_var_lists):
        self.faulty_var = faulty_var
        if not self.error_handler():
            return 0.0
        self.sorted_var_lists = sorted(located_var_lists, key=lambda x: x[1], reverse=True)
        max_weight = max(w for (_, w) in self.sorted_var_lists[:self.vars_limit])
        min_dist = float('inf')
        min_index = -1
        for i, dist in enumerate([abs(self.dists[self.faulty_var][s]) for (s, _) in self.sorted_var_lists[:self.vars_limit] if s in self.dists and self.faulty_var in self.dists[s]]):
            if dist < min_dist:
                min_dist = dist
                min_index = i
        if min_index == -1:
            print('Warning: You have got results with no fault localization even close to the correct var! Maybe you should increase your vars_limit?')
        return self.dist_factor(self.sorted_var_lists[min_index][1] / max_weight, min_dist) if min_index != -1 else 0.0 