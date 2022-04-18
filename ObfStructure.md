# FileLevel
*   1: version
* [4]: transport index
* [6]: map index (see Section)
* [7]: address index
* [8]: poi index
* [9]: routing index
*  18: timestamp (unixformat)
*  32: version again

# Section
*   2: name
* [4]: encoding rules
* [5]: map levels (see MapLevel)

# MapLevel
*    1: max zoom
*    2: min zoom
*    3: left
*    4: right
*    5: top
*    6: bottom
*    7: boxes (see TreeNode)
* [15]: blocks

# TreeNode
*   1: left
*   2: right
*   3: top
*   4: bottom
*   5: map data (see MapBlock)
* [7]: children boxes (see TreeNode)

# MapBlock
*  [7]:
* [15]:


