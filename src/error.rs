//! Error primitives.

use pyo3::{exceptions::PyException, PyErr};
use std::convert::From;

/// Alias result to always return our own error type.
pub(crate) type Result<T> = std::result::Result<T, Error>;

/// Error variants this library might throw.
#[derive(Debug, thiserror::Error)]
pub enum Error {
    #[error("expected header \"{0}\" is missing")]
    MissingHeader(String),
    #[error("error while parsing \"{0}\"")]
    Parsing(String),
}

impl From<Error> for PyErr {
    fn from(err: Error) -> PyErr {
        PyException::new_err(err.to_string())
    }
}
