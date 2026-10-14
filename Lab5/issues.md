\# Static Code Analysis - Issues and Fixes



\## Overview



The original parking permit management program was analyzed using

Pylint, Bandit, and Flake8. The identified issues were addressed to

improve code quality, security, readability, and error handling.



\## Issues Identified



| Issue | Type | Line(s) | Description | Fix Approach |

|---|---|---|---|---|

| Insecure random number generation | Security - Low | 13 | The program used `random.randint()` to generate permit numbers. | Replaced it with `secrets.randbelow()` for security-oriented random number generation. |

| Bare exception handling | Code Quality | 17, 24, 31, 42 | Bare `except` blocks could hide unexpected errors and make debugging difficult. | Replaced broad exception handling with specific exception types and removed unnecessary exception handling. |

| Mutable default argument | Code Quality | 12 | The `zone\_records=\[]` default list could be shared across function calls. | Changed the default to `None` and created a new list when needed. |

| File handling without context managers | Code Quality | 43, 48 | Files were opened without consistently using context managers, risking improper resource cleanup. | Used `with open(...)` and specified UTF-8 encoding. |

| Missing input validation | Reliability | 12–14, 63–67 | Invalid vehicle plates and zone identifiers could be accepted. | Added validation for vehicle plates and allowed zones. |

| Invalid expiry-date handling | Reliability | 29–33, 62 | Incorrect date formats could be silently treated as valid expiry dates. | Added explicit date parsing and validation using the `YYYY-MM-DD` format. |

| Inconsistent function naming | Code Style | 54 | The function `setExpiry` did not follow the recommended `snake\_case` naming convention. | Renamed it to `set\_expiry`. |

| Missing docstrings | Code Quality | Multiple | Functions and the module lacked documentation. | Added module and function docstrings. |

| Formatting violations | Code Style | Multiple | The original file contained spacing problems, long lines, and inconsistent line endings. | Standardized formatting and corrected line endings. |

| Unprotected program entry point | Maintainability | 73 | Calling `main()` directly at module level caused the demonstration to run when the module was imported. | Added an `if \_\_name\_\_ == "\_\_main\_\_":` guard. |



\## Final Static Analysis Results



| Tool | Original Result | Final Result |

|---|---|---|

| Pylint | 6.32/10 | 10.00/10 |

| Bandit | 2 low-severity findings | No issues identified |

| Flake8 | 16 violations | Zero violations |



\## Conclusion



Static code analysis helped identify security, reliability, and

maintainability problems in the original program. The revised

implementation addresses the identified issues and passes all three

static analysis tools.

