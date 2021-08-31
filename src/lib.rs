//! GEF file parsing.
//!
//! Parser `.gef` files into a combination of headers and the measurements body.
//!
//! ## Example
//!
//! ```
//! # fn main() -> Result<(), gef::error::Error> {
//! let gef_file = include_str!("../tests/files/example.gef");
//!
//! let (csv, headers) = gef::parse(&gef_file)?;
//! # Ok(())
//! # }
//! ```

pub mod error;
mod header;
mod nom;

use crate::{error::Result, header::Header};
use itertools::Itertools;
use pyo3::{types::PyModule, PyResult, Python};
use std::collections::HashMap;

/// Type defined for easy use and extra methods.
pub type HeaderMap<'a> = HashMap<&'a str, Vec<Vec<&'a str>>>;

/// Parse a GEF file.
///
/// Return a hashmap of the same headers with the arguments of each line.
pub fn parse(gef: &'_ str) -> Result<(&'_ str, HeaderMap<'_>)> {
    // Parse the errors as a list
    let (data, headers) = header::parse_headers(gef)?;

    // Group the list by the column name, so we'll get an array of array of
    // arguments
    let headers_map = headers
        .into_iter()
        // Create a tuple from the header
        .map(Header::decompose)
        // Group by the column names
        .into_group_map();

    Ok((data, headers_map))
}

/// The python module.
#[pyo3::proc_macro::pymodule]
fn gef(_py: Python, module: &PyModule) -> PyResult<()> {
    // Python wrapper around the parse function.
    #[pyfn(module, name = "parse")]
    fn parse_py(gef: &'_ str) -> PyResult<(&'_ str, HeaderMap<'_>)> {
        // Map the error to a python error
        parse(gef).map_err(|err| err.into())
    }

    Ok(())
}

#[cfg(test)]
mod tests {
    #[test]
    fn example() {
        let (csv, headers) = super::parse(&include_str!("../pygef/files/example.gef")).unwrap();

        assert!(headers.contains_key("GEFID"));
        assert!(headers.contains_key("PROCEDURECODE"));
        assert_eq!(headers["COLUMNVOID"].len(), 9);

        assert!(csv.starts_with("0.0000e+000 9.9990e+003 9.9990e+003 9.9990e+003 9.9990e+003 9.9990e+003 9.9990e+003 9.9990e+003 9.9990e+003"));
    }
}
