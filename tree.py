class TreeNode():
	def __init__(self,data, playerid):
		self.player = data
		self.id = playerid
		self.left = None
		self.right = None
	def read(self):
		return self.data
	def get_children(self):
		return self.left, self.right
	def inorder(self):
		def inorder_helper(node,accum):
			if node == None:
				return
			inorder_helper(node.left,accum)
			accum.append(node)
			print(node)
			inorder_helper(node.right,accum)
		accum = []
		inorder_helper(self,accum)
		return accum 

	def preorder(self):
		def preorder_helper(node,accum):
			if node == None:
				return
			accum.append(node)
			print(node)
			preorder_helper(node.left,accum)
			preorder_helper(node.right,accum)
		accum = []
		preorder_helper(self,accum)
		return accum 
	def postorder(self):
		def postorder_helper(node,accum):
			if node == None:
				return
			postorder_helper(node.left,accum)
			postorder_helper(node.right,accum)
			accum.append(node)
			print(node)
		accum = []
		postorder_helper(self,accum)
		return accum 
