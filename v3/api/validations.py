from schema import Schema, Regex

validation_dictionary = {'create_user': {'email': Regex(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)",
                                                        error="Not a valid email"),
                                         'password': Regex(r'[A-Za-z0-9@#$%^&+=]{8,}',
                                                           error="Password is not compliant with requirements")
                                         },
                         'login': {
                             'email': Regex(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)",
                                            error="Not a valid email"),
                             'password': Regex(r'[A-Za-z0-9@#$%^&+=]{8,}',
                                               error="Password is not compliant with requirements")
                         }
                        }