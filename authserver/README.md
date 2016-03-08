## Build

    make venv
	. venv.authserver/bin/activate
	make init

## Run

Running should work out of the box:

    ./authserver.py

For options, run

    ./authserver.py --help


This starts an authentication endpoint on `https://localhost:<port>/api/auth`
which expects requesters to authenticate via basic authentication following
the [Docker registry-prescribed scheme](https://github.com/docker/distribution/blob/master/docs/spec/auth/token.md).
For example,

    curl --insecure -u john:pAssword https://localhost:8443/api/auth?service=myservice
	
On successful authentication, the response would be a JSON Web Token similar to:

	{
	  "token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IlJXTFI6M1lLWDpYWlNYOjNZUVk6N1RIVDpZQkRROktKUko6V1hZNTpGTVJKOk9NR1g6T0JMTjpEMkNYIn0.eyJpc3MiOiJFbGFzdGlzeXMiLCJhdWQiOiJteXNlcnZpY2UiLCJleHAiOjE0NTc1MzA4NzIsIm5iZiI6MTQ1NzQ0NDQ3Mn0.FsZ8LsnHxdalpebucLU_PxAd7HKC0j-rk_rY1A9FJg-cVTM_FswSs6YC_DSlpdHE1k3c0kvCbSSo1fzG2p__2c3XhYp8IWjuy2xsQugCrBYSNL-X9zOlkpzVLcAr8l7uip6QOt5mhcsJ4jXjGMkJSofPh0JRSNqDP9r9G7GVyeDwQpi2cnpysPCT5M8WDvEfAYmsoFe5s-_CEPkAQ0L9H7Wo0Dl4hkKqU7tuld2MI3FLf2Sv7QdXKQ6E-kMxD8JIMGsLGLpyMpJrg8Fp2ma77v5Bx7kXR_AmyP9_iI5-f1-Ts4XTrV6zquT_BEYc1AKEWDD9T_IbNjdXFS0azIzDokbttf4Y7gAXQNPFu_WOl2zKUlqG9Gweb1k0vGD1L0DS5XJUa-TmPXWpVWyEJIYvIRhmYdSm3Ie4jaTnJZGFt8JTovCxuR0vEEAYITeKrU0KB9JieLOvbakIqzl_ZSUgsn8o5So0m6dYrPsSPAmk01xF7-j_iMRCq0emBzMN0i0OxL51Rc1oZUMJ1sJ7u7yAJ2c_Lj2vo9XQUTaiJ7SE8G5kOSAtNPrEW_7kUH5-8HlJZEkPurBRgzzQTiZImtfHh7YL6gzsqw-wEeBVF_5K1PlC2hIkS_7LsyKfLU-a5PLcETvyYY9BZNZKtS5kDizodQ0-JAuR5xXcapmmH4XffWA"
	}
