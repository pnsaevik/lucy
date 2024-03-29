# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2024-01-10

### Added
- Possible to convert ROMS raw variables to log values when storing
- Standardized schema for tables
- Allow downloading farm data from the Fisheries Directorate
- Script for converting raw ROMS files to NorKyst files

### Changed
- Lice data are no longer extrapolated in time


## [1.0.4] - 2023-09-13

### Added
- Column indicating whether lice data has been interpolated

### Changed
- Lice data are no longer extrapolated in time

### Fixed
- Three or more consecutive gaps in lice data are not filled


## [1.0.3] - 2023-09-11

### Added
- Function for filling in missing lice counts


## [1.0.2] - 2023-09-11

### Added
- Module for downloading data from the Fisheries Directorate


## [1.0.1] - 2023-09-11

### Added
- Auto-generated API reference


## [1.0.0] - 2023-09-11

### Added
- GitHub Actions script
- Changelog
