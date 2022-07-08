# PBF file structure

### FileLevel
*   int32-bigendian: size of BlobHeader
*   bytes[]: BlobHeader

### BlobHeader
*  1: type (string)
*  3: datasize

### BlobData
*  2: uncompressed size
*  3: zlib compression

### OsmHeader
*   1: seq     HeaderBBox
* [4]: seq     reqFeatures
*  16: seq     source program
*  32: varint  timestamp
*  33: varint  replication
*  34: seq     url

### DataBlock
*   1:  string table
* [2]:  group

### DataGroup:
*   2: seq  dense nodes
* [3]: seq  ways
* [4]: seq  relations

### DenseNodes
*  1: seq  ids (delta pack)
*  5: seq
*  8: seq  lats (delta packs)
*  9: seq  lons (delta packs)
* 10: seq  keys and values

### Way
*  1: varint id
*  2: seq  keys
*  3: seq  vals
*  4: seq
*  8: seq  refs (delta packs)
