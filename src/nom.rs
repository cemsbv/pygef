//! Tools and utilities for the nom crate.

use nom::error::VerboseError;

/// Remove a lot of boilerplate for nom, use the verbose error type for span
/// information.
pub(crate) type IResult<'a, T> = nom::IResult<&'a str, T, VerboseError<&'a str>>;
