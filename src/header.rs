//! Header parsing.

use crate::{
    error::{Error, Result},
    nom::IResult,
};

/// Separator used between values in the GEF file.
const VALUE_SEPARATOR: char = ',';

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
            nom::character::complete::alphanumeric1,
        )(s)?;

        let (s, values) = nom::sequence::preceded(
            // Take all whitespace between the column header name and the = symbol
            nom::character::complete::space0,
            nom::branch::alt((
                // Get the values between the '=' char and the end of the line
                nom::sequence::preceded(
                    // Take all spaces and = characters
                    nom::bytes::complete::tag("= "),
                    nom::error::context(
                        "the header values",
                        // Get the comma-space separated values
                        nom::multi::separated_list0(
                            // Get until the ',' character and trim the spaces
                            nom::sequence::delimited(
                                nom::character::complete::space0,
                                nom::character::complete::char(VALUE_SEPARATOR),
                                nom::character::complete::space0,
                            ),
                            // Take until the end of the line or until a separator is found
                            nom::bytes::complete::take_till(|c: char| {
                                c == VALUE_SEPARATOR || c.is_control()
                            }),
                        ),
                    ),
                ),
                // Don't return any values if the rest of the line is just '='
                nom::combinator::map(nom::character::complete::char('='), |_| vec![]),
            )),
        )(s)?;

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
            Header::from_str("A = 1").unwrap().1,
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

    #[test]
    fn test_gef_file() {
        let (csv, _) = parse_headers(
            "
#GEFID = 1,1,0
#COLUMNTEXT = 1, aan
#COLUMNSEPARATOR = ;
#RECORDSEPARATOR = !
#FILEOWNER = DINO
#FILEDATE = 2010,9,1
#PROJECTID = DINO-BOR
#COLUMN = 9
#COLUMNINFO = 1, m, Diepte bovenkant laag, 1
#COLUMNINFO = 2, m, Diepte onderkant laag, 2
#COLUMNINFO = 3, mm, Zandmediaan, 8
#COLUMNINFO = 4, mm, Grindmediaan, 9
#COLUMNINFO = 5, %, Lutum percentage, 3
#COLUMNINFO = 6, %, Silt percentage, 4
#COLUMNINFO = 7, %, Zand percentage, 5
#COLUMNINFO = 8, %, Grind percentage, 6
#COLUMNINFO = 9, %, Organische stof percentage, 7
#COLUMNVOID = 1, -9999.99
#COLUMNVOID = 2, -9999.99
#COLUMNVOID = 3, -9999.99
#COLUMNVOID = 4, -9999.99
#COLUMNVOID = 5, -9999.99
#COLUMNVOID = 6, -9999.99
#COLUMNVOID = 7, -9999.99
#COLUMNVOID = 8, -9999.99
#COLUMNVOID = 9, -9999.99
#LASTSCAN = 44
#REPORTCODE = GEF-BORE-Report,1,0,0
#MEASUREMENTCODE = Onbekend
#TESTID = B25G0304
#XYID = 31000,120870,483400
#ZID = 31000,2.0
#MEASUREMENTVAR = 19, 1, -, aantal peilbuizen
#EOH =
0.00;1.20;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;'Zgh2';'TGR \
             GE';'ZMFO';'CA3';!
1.20;3.10;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;'Zg';'ON';'ZMGO';'FN2';'\
             CA2';!
3
",
        )
        .unwrap();

        assert_eq!(
            csv,
            "0.00;1.20;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;'Zgh2';'TGR \
             GE';'ZMFO';'CA3';!
1.20;3.10;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;'Zg';'ON';'ZMGO';'FN2';'\
             CA2';!
3
"
        );
    }
}
