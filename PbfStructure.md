# PBF file structure

### FileLevel
*   int32-bigendian: size of OsmHeader
*   bytes[]: OsmHeader

### BlobHeader
*  1: type (string)
*  3: datasize

### BlobData
*  2: uncompressed size
*  3: zlib compression
