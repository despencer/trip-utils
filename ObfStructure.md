# OBF file structure

### FileLevel
*   1: version
* [4]: transport index
* [6]: map index (see Section)
* [7]: address index
* [8]: poi index
* [9]: routing index
*  18: timestamp (unixformat)
*  32: version again

### Section
Loaded by *ObfMapSectionReader_P::read*
*   2: name
* [4]: encoding rules
* [5]: map levels (see MapLevel)

The main entrance to the map data reader is the *ObfMapSectionReader_P::loadMapObjects* function.
It does in sequence node collection, node sorting by file offset, and data acquisition

#### Node Collection
*readMapLevelTreeNodes* locates root node (MapLevel::7) and calls *readTreeNode* inside this blob (of *TreeNode* structure).
Then if root node contains data (TreeNode::5) it added to data nodes list.
For chilren nodes (TreeNode::7) *readTreeNodeChildren* is called. It recursive calls itself with a help of *readTreeNode* for box data.

#### Data acquisition
Performed by the function *readMapObjectsBlock* for the map data (TreeNode::5)

### MapLevel
*    1: max zoom
*    2: min zoom
*    3: left
*    4: right
*    5: top
*    6: bottom
*    7: root node (see TreeNode)
* [15]: blocks

### TreeNode
*   1: left
*   2: right
*   3: top
*   4: bottom
*   5: map data pointer, not a blob! (see MapBlock)
* [7]: children boxes (see TreeNode)

### MapBlock
*   10: baseId
* [12]: dataObjects (see MapObject)
*   15: StringTable

### MapObject
*   1: seq   coordinates
*   2: seq
*   4: seq
*   6: seq
*   7: seq   types
*   8: seq
*  10: seq
*  12: varint


### StringTable
*  [1]: string
