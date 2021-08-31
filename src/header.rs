//! Header parsing.

use crate::{
    error::{Error, Result},
    nom::IResult,
};

/// References to the strings of the file where the header is and it's values.
#[derive(Debug, Clone, PartialEq)]
pub struct Header<'a> {
    /// The part following the '#' until the '=' symbol.
    pub name: &'a str,
    /// Comma separated values following the first '=' symbol of the line.
    pub values: Vec<&'a str>,
}

impl<'a> Header<'a> {
    /// Create a tuple from the name and the values.
    pub fn decompose(self) -> (&'a str, Vec<&'a str>) {
        (self.name, self.values)
    }

    /// Parse a header string.
    ///
    /// The string shouldn't contain a '#' character at the begin nor a newline
    /// at the end.
    fn from_str(s: &'a str) -> IResult<Self> {
        // Get the name of the header, the left hand side
        let (s, name) = nom::error::context(
            "the name of the header",
            nom::bytes::complete::take_until("="),
        )(s)?;

        let (s, values) = nom::branch::alt((
            // Get the values between the '=' char and the end of the line
            nom::sequence::preceded(
                nom::bytes::complete::tag("= "),
                nom::error::context(
                    "the header values",
                    // Get the comma-space separated values
                    nom::multi::separated_list0(
                        nom::bytes::complete::tag(", "),
                        nom::bytes::complete::take_till(|c| c == ',' || c == '\n'),
                    ),
                ),
            ),
            // Don't return any values if the rest of the line is just '='
            nom::combinator::map(nom::character::complete::char('='), |_| vec![]),
        ))(s)?;

        Ok((s, Self { name, values }))
    }
}

/// Parse the headers of the GEF file.
///
/// Return the parsed headers and a reference to the rest of the file.
pub(crate) fn parse_headers(gef: &'_ str) -> Result<(&'_ str, Vec<Header<'_>>)> {
    nom::sequence::preceded(
        // Ignore the whitespace before the first header line
        nom::character::complete::multispace0,
        // Loop over all sequences starting with # until the newline character
        nom::multi::many0(nom::error::context(
            "a header line",
            nom::sequence::delimited(
                nom::character::complete::char('#'),
                Header::from_str,
                nom::character::complete::newline,
            ),
        )),
    )(gef)
    // Convert the nom error to our own error type
    .map_err(|err| Error::Parsing(err.to_string()))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_single_header() {
        assert_eq!(
            Header::from_str("A= 1").unwrap().1,
            Header {
                name: "A",
                values: vec!["1"]
            }
        );

        assert_eq!(
            Header::from_str("A= 1, 2").unwrap().1,
            Header {
                name: "A",
                values: vec!["1", "2"]
            }
        );
    }

    #[test]
    fn test_empty_header() {
        assert_eq!(
            Header::from_str("A=").unwrap().1,
            Header {
                name: "A",
                values: vec![]
            }
        );

        let (rest, headers) = parse_headers("#A=\nrest").unwrap();
        assert_eq!(rest, "rest");
        assert_eq!(
            headers,
            vec![Header {
                name: "A",
                values: vec![]
            },]
        );
    }

    #[test]
    fn test_header_names() {
        let (rest, headers) = parse_headers("#A= 1\n#B= 2\nrest").unwrap();

        assert_eq!(rest, "rest");
        assert_eq!(
            headers,
            vec![
                Header {
                    name: "A",
                    values: vec!["1"]
                },
                Header {
                    name: "B",
                    values: vec!["2"]
                }
            ]
        );
    }

    #[test]
    fn test_whitespace_prefix() {
        let (rest, headers) = parse_headers("\n\t\n  \n#A= 1\n#B= 2\nrest").unwrap();

        assert_eq!(rest, "rest");
        assert_eq!(
            headers,
            vec![
                Header {
                    name: "A",
                    values: vec!["1"]
                },
                Header {
                    name: "B",
                    values: vec!["2"]
                }
            ]
        );
    }
}
