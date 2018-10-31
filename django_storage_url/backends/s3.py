import six
import furl
from storages.backends import s3boto3


class S3Storage(s3boto3.S3Boto3Storage):
    def __init__(self, dsn):
        endpoint = dsn.host.rsplit('.', 3)
        bucket_name = endpoint[0]
        storage_host = '.'.join(endpoint[1:])

        addressing_style = dsn.args.get("addressing_style")
        if not addressing_style:
            if "." in bucket_name:
                addressing_style = "path"
            else:
                addressing_style = "auto"

        if "url" in dsn.args:
            base_url = furl.furl(dsn.args.get("url"))

            url_protocol = base_url.scheme
            secure_urls = url_protocol == "https"
            custom_domain = base_url.netloc
        else:
            # base_url = furl.furl(
            #     scheme=""
            # )

            secure_urls = True
            url_protocol = "https"
            custom_domain = dsn.args.get("domain")

        location = six.text_type(dsn.path).lstrip("/")

        super(S3Storage, self).__init__(
            access_key=dsn.username or '',
            secret_key=dsn.password or '',
            bucket_name=bucket_name,
            use_ssl=True,
            endpoint_url="https://{}/".format(storage_host),
            addressing_style=addressing_style,
            signature_version=dsn.args.get('auth', None),
            location=location,
            custom_domain=custom_domain,
            # TODO: Make the default `private` and explicitly set the ACL to
            #       `public-read` during provisioning
            default_acl=dsn.args.get("acl", "public-read"),
            # TODO: Allow to be set (especially once we support private ACLs)
            querystring_auth=False,
            url_protocol=url_protocol,
            secure_urls=secure_urls,
            # TODO: Enforce encryption everywhere. Check status on non-AWS
            #       providers.
            # encryption=True,
            max_memory_size=10 * 1024 ** 2  # Roll over to disk after 10 MB
        )
