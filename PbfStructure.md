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