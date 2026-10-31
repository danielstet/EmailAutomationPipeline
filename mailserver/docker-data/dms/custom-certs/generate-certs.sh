#! /bin/sh
mkdir -p demoCA

step certificate create "Smallstep Root CA" "demoCA/cacert.pem" "demoCA/cakey.pem" \
  --no-password --insecure \
  --profile root-ca \
  --not-before "2021-01-01T00:00:00+00:00" \
  --not-after "2031-01-01T00:00:00+00:00" \
  --san "localmail.test" \
  --san "mail.localmail.test" \
  --kty RSA --size 2048

step certificate create "Smallstep Leaf" mail.localmail.test-cert.pem mail.localmail.test-key.pem \
  --no-password --insecure \
  --profile leaf \
  --ca "demoCA/cacert.pem" \
  --ca-key "demoCA/cakey.pem" \
  --not-before "2021-01-01T00:00:00+00:00" \
  --not-after "2031-01-01T00:00:00+00:00" \
  --san "localmail.test" \
  --san "mail.localmail.test" \
  --kty RSA --size 2048
