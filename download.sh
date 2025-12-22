git clone --depth 1 'https://user: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@github.com/seo888/SeoApi_bak.git' ./_tmp_clone
# rm -rf ./_tmp_clone/src
# rm -rf ./_tmp_clone/templates
# rm -rf ./_tmp_clone/.gitignore
# rm -rf ./_tmp_clone/Cargo.toml
# rm -rf ./_tmp_clone/Cargo.lock
# rm -rf ./_tmp_clone/ip.txt
# rm -rf ./_tmp_clone/打包命令.txt
rm -rf ./_tmp_clone/.git
rsync -a --delete ./_tmp_clone/ ./app/
echo "Download completed."
rm -rf ./_tmp_clone