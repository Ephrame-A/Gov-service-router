import "next-auth";

declare module "next-auth" {
  interface Session {
    accessToken?: string;
    user?: {
      name?: string | null;
      email?: string | null;
      image?: string | null;
      role?: string;
      institutionId?: string;
    };
  }

  interface User {
    role?: string;
    institutionId?: string;
    accessToken?: string;
  }
}

declare module "next-auth/jwt" {
  interface JWT {
    role?: string;
    institutionId?: string;
    accessToken?: string;
  }
}
