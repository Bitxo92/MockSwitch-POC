export interface MockCredential {
  username: string;
  password: string;
  user: {
    sub: string;
    name: string;
    email: string;
    given_name: string;
    family_name: string;
    email_verified: boolean;
  };
  realm_access: { roles: string[] };
  resource_access: {
    app: { roles: string[] };
    api: { roles: string[] };
    account: { roles: string[] };
  };
}

export const MOCK_CREDENTIALS: MockCredential[] = [
  {
    username: "user",
    password: "user",
    user: {
      sub: "mock-jdoe-id",
      name: "Joseph Doe",
      email: "jdoe@mock.dev",
      given_name: "Joseph",
      family_name: "Doe",
      email_verified: true,
    },
    realm_access: {
      roles: ["offline_access", "uma_authorization", "default-roles-main"],
    },
    resource_access: {
      app: {
        roles: ["password_management"],
      },
      api: {
        roles: ["keycloak-admin"],
      },
      account: {
        roles: ["manage-account", "manage-account-links", "view-profile"],
      },
    },
  },
  {
    username: "operario",
    password: "operario",
    user: {
      sub: "mock-operario-id",
      name: "Operario Mock",
      email: "operario@mock.dev",
      given_name: "Operario",
      family_name: "Mock",
      email_verified: true,
    },
    realm_access: {
      roles: ["offline_access", "uma_authorization", "default-roles-main"],
    },
    resource_access: {
      app: {
        roles: ["detector_metales-accesso"],
      },
      api: {
        roles: ["hoja_control-read", "linea_cierre-read"],
      },
      account: {
        roles: ["manage-account", "view-profile"],
      },
    },
  },
];
