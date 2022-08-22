import pkg_resources

try:
    __version__ = pkg_resources.get_distribution("pygef").version
# during CI
except pkg_resources.DistributionNotFound:
    __version__ = "unknown"
